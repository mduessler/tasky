# Root-directory
root-dir=$(shell pwd)

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
aws-user-admin=tasky-admin
aws-user-dev=tasky-dev

prod-image=tms-prod-nginx:test 


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

tests: unit-tests security-tests

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

# Test production images modules on vulnerabilities
#
security-tests: build
	# Build production images
	docker build -f prod/Dockerfile.nginx -t tms-prod-nginx:test ./prod/

	# Test pip audit
	docker run --rm --entrypoint pip tms-prod:test freeze | poetry run pip-audit -r /dev/stdin

	# Test production images with trivy
	docker run --rm \
		-v $(docker-socket):/var/run/docker.sock \
		-v trivy-cache:/root/.cache/trivy \
		aquasec/trivy image tms-prod:test
	docker run --rm \
		-v $(docker-socket):/var/run/docker.sock \
		-v trivy-cache:/root/.cache/trivy \
		aquasec/trivy image tms-prod-nginx:test

	# clean up
	docker image rm -f $(prod-image) tms-prod-nginx:test
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
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/gitlab-runner install

destroy-gitlab-runner:
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/gitlab-runner destroy
