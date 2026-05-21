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
terraform-dir=infrastructure/terraform
ansible-dir=infrastructure/ansible

gitlab-runner-dir=environment/dev/gitlab-runner


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
# Infrastructure commands
#
# Set up backend
#

bootstrap-create:
	export TF_VAR_owner_id=$(aws_account_id)
	export AWS_PROFILE=$(aws-user-admin)
	./infrastructure/scripts/bootstrap create

bootstrap-destroy:
	./infrastructure/scripts/bootstrap destroy

# Set up gitlab-runner
# aws s3api head-bucket --bucket ansible-ssm-REDACTED_AWS_ACCOUNT-dev --profile tasky-dev 2> /dev/null
.ONESHELL:
install-gitlab-runner:
	cd $(terraform-dir)/$(gitlab-runner-dir)
	export TF_VAR_owner_id=$(aws_account_id)
	export AWS_PROFILE=$(aws-user-dev)
	read -p "Runner name: " runner_name && \
	export TF_VAR_runner_name=$$runner_name && \
	terraform init -reconfigure \
		-backend-config="bucket=tasky-terraform-state-$(aws_account_id)-dev" \
		-backend-config="key=runner/dev/$$runner_name/terraform.tfstate" && \
	terraform apply || exit 1

	cd $(root-dir)
	cd $(ansible-dir)/$(gitlab-runner-dir) && \
	ansible-galaxy collection install -r requirements.yaml -p ./collections && \
	read -p "Runner token: " runner_token && echo && \
	ANSIBLE_CONFIG=./ansible.cfg ansible-playbook playbook.yaml \
		-i inventory/aws_ec2.yaml \
		-l "runner_dev_$$runner_name" \
		-e runner_name="$$runner_name" \
		-e runner_token="$$runner_token" \
		-e owner_id="$(aws_account_id)" -vvvv

.ONESHELL:
terraform-destroy-runner:
	cd $(terraform-dir)/$(gitlab-runner-dir)
	export TF_VAR_owner_id=$(aws_account_id)
	export AWS_PROFILE=$(aws-user-dev)
	terraform init -migrate-state\
		-backend-config="bucket=tasky-terraform-state-REDACTED_AWS_ACCOUNT-dev" \
		-backend-config="key=dev/terraform.tfstate"
	terraform destroy --auto-approve
