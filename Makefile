# Root-directory
root-dir=$(shell pwd)
env-file=.env.dev
project-name=tasky


# dev
service-dev=tms-dev
file-dev=dev/docker-compose.yaml
database-dev=postgres
apps=user tms_auth task registration
poetry-version=2.2.1

cert-path-dev=dev/certs
cert-subj=/CN=localhost

test-data=/home/tms/web/tests/data
docs = ./docs/
docker-socket = $(shell docker context inspect --format '{{.Endpoints.docker.Host}}' | sed 's|unix://||')

packer-dir = ./infrastructure/packer/environment/dev/gitlab-runner/
owner_id:=$(shell grep -m1 '^TF_VAR_owner_id=' $(env-file) | cut -d= -f2-)
aws-user-admin=tasky-admin
aws-user-dev=tasky-dev

prod-image=tasky:test
nginx-image=tasky-nginx:test
dockle-image=goodwithtech/dockle:latest


.SILENT:
.ONESHELL:

#
# Commands to run dev environment
#
up-dev:
	./scripts/init-env "dev"
	docker compose --file $(file-dev) up -d
	echo "Checking connection to database..."
	while ! docker compose --file $(file-dev) exec $(service-dev) python manage.py check --database default; do
		sleep 1
	done
	echo "$(service-dev) is healthy."
	docker compose --file $(file-dev) exec $(service-dev) python manage.py clean_tokens

run-dev: up-dev
	docker compose --file $(file-dev) logs -f

makemigrations: up-dev
	docker compose --file $(file-dev) exec $(service-dev) python manage.py makemigrations --no-input $(apps)
	docker compose --file $(file-dev) down

seed-dev:
	echo "Checking connection to database..."
	if ! docker compose --file $(file-dev) exec $(service-dev) python manage.py check --database default; then
		echo "No running test service found."
		exit 1
	fi

	docker compose --file $(file-dev) exec $(service-dev) python manage.py import_user
	docker compose --file $(file-dev) exec $(service-dev) python manage.py loaddata $(test-data)/task/tasks.json
	docker compose --file $(file-dev) exec $(service-dev) python manage.py loaddata $(test-data)/task/task_memberships.json
	docker compose --file $(file-dev) exec $(service-dev) python manage.py loaddata $(test-data)/task/task_notes.json


# Command to run the  application the first time.
#

first-run: gen-cert-dev up-dev seed-dev run-dev

#
# Destroy and clean dev relicts
#
down-dev:
	docker compose --file $(file-dev) down
stop-dev:
	docker compose --file $(file-dev) stop

clean-dev: stop-dev
	docker compose --file $(file-dev) rm -f $(service-dev)
	docker image rm $(service-dev)

full-clean-dev: stop-dev
	docker compose --file $(file-dev) rm -f
	docker image rm $(service-dev) $(database-dev)
	docker volume rm $(service-dev)-db

#
# Kubernetes dev
#

# Create dev cluster
#
create-cluster-dev:
	k3d cluster create $(CLUSTER) -p "8080:80@loadbalancer" -p "8443:443@loadbalancer" || true

# Delete dev cluster
#
delete-dev-env:
	k3d cluster delete $(project-name)-dev


#
# Build production environment
#

# Build production main image
#
build:
	docker build -f prod/Dockerfile -t $(prod-image) .


#
# Tests
#
# Full tests (without timing)
#

tests: unit-tests test-image security-tests

# Unit tests without timing
#

unit-tests: up-dev
	docker compose --file $(file-dev) exec $(service-dev) pytest -m "not timing"
	docker compose --file $(file-dev) stop

# Unit test with timing
#

unit-tests-full: up-dev
	docker compose --file $(file-dev) exec $(service-dev) pytest timing
	docker compose --file $(file-dev) stop

# Test production image
#
test-image: build
	export PROD_IMAGE=$(prod-image)
	./prod/tests/test-main-image

	export ENV_FILE=$(env-file)

	docker network create tasky-prod-net-test >/dev/null 2>&1
	docker run -d \
		--name tasky-prod-db-test \
		--network tasky-prod-net-test \
		--env-file $(env-file) \
		-e POSTGRES_PASSWORD="postgres" \
		postgres:18.4-alpine  >/dev/null 2>&1

	./prod/tests/test-runtime-hardend
	./prod/tests/test-django-readiness

	docker image rm -f $(prod-image) >/dev/null 2>&1
	docker rm -f tasky-prod-db-test >/dev/null 2>&1
	docker network rm tasky-prod-net-test >/dev/null 2>&1

# Test production images modules on vulnerabilities
#
security-tests: build
	# Build production images
	docker build -f prod/Dockerfile.nginx -t $(nginx-image) ./prod/

	export DOCKER_SOCKET=$(docker-socket)
	export DOCKLE_IMAGE=$(dockle-image)
	export PROD_IMAGE=$(prod-image)
	export PROD_NGINX_IMAGE=$(nginx-image)

	./prod/tests/test-security

	# clean up
	docker image rm -f $(prod-image) $(nginx-image)
	docker volume rm trivy-cache

# Test dev image with trivy
#
security-scan-dev:
	docker build -f dev/Dockerfile.ci -t tms:ci .

	docker run --rm \
		-v $(docker-socket):/var/run/docker.sock \
		-v trivy-cache:/root/.cache/trivy \
		aquasec/trivy image tms:ci

	docker image rm -f tms:ci
	docker volume rm trivy-cache


#
# Generate file objects
#
# Generate OpenAPI specification
#

openapi:
	poetry run python task_management_system/manage.py spectacular --file $(docs)/openapi.yaml

# Generate Certificats for Lets Encrypt
#

gen-cert-dev:
	mkdir -p $(cert-path-dev)
	openssl req -x509 -nodes -days 365 \
		-newkey rsa:2048 \
		-keyout $(cert-path-dev)/local.key \
		-out $(cert-path-dev)/local.crt \
		-subj "$(cert-subj)"

#
# Local Development components
#
# Install poetry
#

poetry:
	pipx install poetry==$(poetry-version)

# Install pre-commit
#

pre-commit:
	poetry install
	poetry run pre-commit install


#
# Infrastructure commands
#
# Create backend
#

bootstrap-create:
	export AWS_PROFILE=$(aws-user-admin)
	./infrastructure/scripts/bootstrap create

bootstrap-destroy:
	./infrastructure/scripts/bootstrap destroy


# Create AMI gitlab-runner image
#

create-runner-img:
	cd $(packer-dir)
	export AWS_PROFILE=$(aws-user-admin)
	packer init .
	packer build gitlab-runner.pkr.hcl


# Commands to install or destroy a gitlab-runner
#

install-gitlab-runner:
	export TF_VAR_owner_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/gitlab-runner install

destroy-gitlab-runner:
	export TF_VAR_owner_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/gitlab-runner destroy
