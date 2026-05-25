# Root-directory
root-dir=$(shell pwd)

ENV ?=

ifeq ($(filter dev prod,$(ENV)),$(ENV))
  ENV_FILE := .env.$(ENV)
else
  ENV_FILE := .env
endif

-include $(ENV_FILE)
export

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

aws-user-admin=tasky-admin
aws-user-dev=tasky-dev

#
# Commands to run dev environment
#
.SILENT:
.ONESHELL:
up-dev:
	./scripts/init-env
	docker compose --file $(file-dev) up -d
	echo "Checking connection to database..."
	while ! docker compose --file $(file-dev) exec $(service-dev) python manage.py check --database default; do
		sleep 1
	done
	echo "$(service-dev) is healthy."
	docker compose --file $(file-dev) exec $(service-dev) python manage.py clean_tokens

run-dev: up-dev
	docker compose --file $(file-dev) logs -f

makemigrations:
	docker compose --file $(file-dev) exec $(service-dev) python manage.py makemigrations --no-input $(apps)

.ONESHELL:
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


#
# Destroy and clean dev relicts
#
down-dev:
	docker compose --file $(file-dev) down
.SILENT:
stop-dev:
	docker compose --file $(file-dev) stop

.SILENT:
clean-dev: stop-dev
	docker compose --file $(file-dev) rm -f $(service-dev)
	docker image rm $(service-dev)

.SILENT:
full-clean-dev: stop-dev
	docker compose --file $(file-dev) rm -f
	docker image rm $(service-dev) $(database-dev)
	docker volume rm $(service-dev)-db


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

# Test python modules on vulnerabilities
#
.ONESHELL:
security-tests:
	# Build production images
	docker build -f prod/Dockerfile -t tms-prod:test .
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
	docker image rm -f tms-prod:test tms-prod-nginx:test
	docker volume rm trivy-cache

# Test dev image with trivy
#
security-scan-dev:
	docker build -f prod/Dockerfile.ci -t tms:ci .

	docker run --rm \
		-v $(docker-socket):/var/run/docker.sock \
		-v trivy-cache:/root/.cache/trivy \
		aquasec/trivy image tms:ci

docker image rm -f tms:ci
	docker volume rm trivy-cache


#
# Generate file objects
#
# Generate OpenAPI specfication
#

openapi:
	poetry run python task_management_system/manage.py spectacular --file $(docs)/openapi.yaml

# Generate Certificats for Lets Encrypt
#

.ONESHELL:
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

.ONESHELL:
create-runner-img:
	cd $(packer-dir)
	export AWS_PROFILE=$(aws-user-admin)
	packer init .
	packer build gitlab-runner.pkr.hcl


# Commands to install or destroy a gitlab-runner
#

.ONESHELL:
install-gitlab-runner:
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/gitlab-runner install

.ONESHELL:
destroy-gitlab-runner:
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/gitlab-runner destroy
