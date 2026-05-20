# Root-directory
root-dir=./task_management_system/

# dev
service-dev=tms-dev
file-dev=dev/docker-compose.yaml
database-dev=postgres
apps=user tms_auth task registration

cert-path-dev=dev/certs
cert-subj=/CN=localhost

test-data=/home/tms/web/tests/data
docs = ./docs/

terraform-dir=infastructure/terraform/
gitlab-runner-dir=$(terraform-dir)/environment/dev/gitlab-runner

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

tests: up-dev
	docker compose --file $(file-dev) exec $(service-dev) pytest
	docker compose --file $(file-dev) stop

tests-full: up-dev
	docker compose --file $(file-dev) exec $(service-dev) pytest timing
	docker compose --file $(file-dev) stop

.ONESHELL:
gen-cert-dev:
	mkdir -p $(cert-path-dev)
	openssl req -x509 -nodes -days 365 \
		-newkey rsa:2048 \
		-keyout $(cert-path-dev)/local.key \
		-out $(cert-path-dev)/local.crt \
		-subj "$(cert-subj)"

openapi:
	poetry run python task_management_system/manage.py spectacular --file $(docs)/openapi.yaml

pre-commit:
	poetry install
	poetry run pre-commit install


#
# Infastructure commands
#
# Set up backend
.ONESHELL:
terraform-init-bootstrap:
	cd $(terraform-dir)/bootstrap
	terraform init
	terraform apply

.ONESHELL:
terraform-destroy-bootstrap:
	cd $(terraform-dir)/bootstrap
	terraform init
	terraform destroy --auto-approve

# Set up gitlab-runner
.ONESHELL:
terraform-init-runner-dev:
	@read -p "Runner name: " runner_name && \
	export TF_VAR_runner_name=$$runner_name && \
	terraform init \
	  -backend-config="bucket=tasky-terraform-state-REDACTED_AWS_ACCOUNT-dev" \
	  -backend-config="key=dev/terraform.tfstate" && \
	terraform apply

.ONESHELL:
terraform-destroy-runner:
	cd $(gitlab-runner-dir)
	terraform init \
	  -backend-config="bucket=tasky-terraform-state-REDACTED_AWS_ACCOUNT-dev" \
	  -backend-config="key=dev/terraform.tfstate"
	terraform destroy --auto-approve
