# Root-directory
root-dir=$(shell pwd)

# dev
service-dev=tms-dev
file-dev=dev/docker-compose.yaml
database-dev=postgres
apps=user tms_auth task registration

cert-path-dev=dev/certs
cert-subj=/CN=localhost

test-data=/home/tms/web/tests/data
docs = ./docs/

aws_account_id=REDACTED_AWS_ACCOUNT
aws-user-admin=tasky-admin
aws-user-dev=tasky-dev

#
# Commands to run dev environment
#
.SILENT:
.ONESHELL:
up-dev:
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
# Tests without timing
#

tests: up-dev
	docker compose --file $(file-dev) exec $(service-dev) pytest
	docker compose --file $(file-dev) stop

# Test with timing
#

tests-full: up-dev
	docker compose --file $(file-dev) exec $(service-dev) pytest timing
	docker compose --file $(file-dev) stop

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
# Lokal Development components
#
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
	export TF_VAR_owner_id=$(aws_account_id)
	export AWS_PROFILE=$(aws-user-admin)
	./infrastructure/scripts/bootstrap create

bootstrap-destroy:
	./infrastructure/scripts/bootstrap destroy


# Create AMI gitlab-runner image
#

ONESHELL:
create-runner-img:
	cd $(packer-dir)
	export AWS_PROFILE=$(aws-user-admin)
	packer init .
	packer build gitlab-runner.pkr.hcl


# Commands to install or destroy a gitlab-runner
#

.ONESHELL:
install-gitlab-runner:
	export TF_VAR_owner_id=$(aws_account_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/gitlab-runner install

.ONESHELL:
destroy-gitlab-runner:
	export TF_VAR_owner_id=$(aws_account_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/gitlab-runner destroy
