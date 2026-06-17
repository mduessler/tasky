# Root-directory
root-dir=$(shell pwd)
env-file=.env.dev
project-name=tasky

# Base
#
chart = deploy/helm/tasky
apps=user tms_auth task registration
docs = ./docs/

# Dev environment
#

poetry-version=2.2.1

# Cluster
cluster-dev = tasky-dev
api-image-dev = tasky:latest
nginx-image-dev = tasky-nginx:latest
helm-values-dev   = -f dev/deploy/helm/tasky/values.yaml -f dev/deploy/helm/tasky/values.local.yaml
ns-dev = $(shell grep '^environment:' dev/deploy/helm/tasky/values.yaml | awk '{print $$2}')
test-data=/home/tms/web/tests/data

# docker compose
service-dev=tasky-api-dev
file-dev=dev/docker-compose.yaml

# Certs
cert-path-dev=dev/certs
cert-subj=/CN=localhost

# Get docker socket
docker-socket = $(shell docker context inspect --format '{{.Endpoints.docker.Host}}' | sed 's|unix://||')

# Infrastructure environment
#
packer-root = ./infrastructure/packer
aws-user-admin=tasky-admin
aws-user-dev=tasky-dev
aws-user-prod-network=tasky-admin
aws-user-prod-kube=tasky-admin
aws-user-prod-packer=tasky-admin

# Development
packer-runner-dir=$(packer-root)/environment/dev/gitlab-runner/
owner_id:=$(shell grep -m1 '^TF_VAR_account_id=' $(env-file) | cut -d= -f2-)

# Production
packer-node-dir=$(packer-root)/environment/prod/kube-node/

prod-image=tasky:test
nginx-image=tasky-nginx:test
dockle-image=goodwithtech/dockle:latest

.SILENT:
.ONESHELL:

#
# Commands to run dev environment
#

# Create dev cluster
create-cluster-dev:
	kind get clusters | grep -q "^$(cluster-dev)$$" \
		|| kind create cluster --name $(cluster-dev) --config dev/kind-config.yaml

# Build images for dev cluster
build-images-dev:
	docker build -f dev/Dockerfile -t $(api-image-dev) .
	docker build -f dev/Dockerfile.nginx -t $(nginx-image-dev) dev
	kind load docker-image $(api-image-dev) $(nginx-image-dev) --name $(cluster-dev)

# Deploy / upgrade the chart
deploy-dev: build-images-dev
	helm upgrade --install tasky $(chart) \
		-n $(ns-dev) --create-namespace \
		-f dev/deploy/helm/tasky/values.yaml \
		-f dev/deploy/helm/tasky/values.local.yaml
	kubectl rollout restart deployment -n $(ns-dev)
	echo "Waiting for api to become ready..."
	kubectl rollout status deployment/tasky-api -n $(ns-dev) --timeout=180s

# Make migrations
makemigrations:
	docker compose --file $(file-dev) up -d
	docker compose --file $(file-dev) exec $(service-dev) python manage.py makemigrations --no-input $(apps)
	docker compose --file $(file-dev) down

# Clean tokens
clean-tokens-dev:
	kubectl exec -n $(ns-dev) deploy/tasky-api -- python manage.py clean_tokens

# Seed database dev
seed-dev:
	kubectl exec -n $(ns-dev) deploy/tasky-api -- python manage.py import_user
	kubectl exec -n $(ns-dev) deploy/tasky-api -- python manage.py loaddata $(test-data)/task/tasks.json
	kubectl exec -n $(ns-dev) deploy/tasky-api -- python manage.py loaddata $(test-data)/task/task_memberships.json
	kubectl exec -n $(ns-dev) deploy/tasky-api -- python manage.py loaddata $(test-data)/task/task_notes.json

# Command to run the  application the first time.
first-run: gen-cert-dev up-dev clean-tokens-dev seed-dev
	kubectl get pods -n $(ns-dev)

# Run dev cluster
up-dev: create-cluster-dev deploy-dev

# Delete dev cluster
delete-cluster-dev:
	kind delete cluster --name $(cluster-dev)
	docker image rm $(api-image-dev) $(nginx-image-dev)


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
tests: unit-tests test-image security-tests

# Unit tests without timing
unit-tests:
	docker compose --file $(file-dev) up -d
	docker compose --file $(file-dev) exec $(service-dev) pytest -m "not timing"
	docker compose --file $(file-dev) stop
	docker compose --file $(file-dev) down

# Unit test with timing
unit-tests-full:
	docker compose --file $(file-dev) up -d
	docker compose --file $(file-dev) exec $(service-dev) pytest timing
	docker compose --file $(file-dev) stop
	docker compose --file $(file-dev) down

# Command do delete all dev docker compose images
clean-dev:
	docker compose --file $(file-dev) down --rmi all


# Test production image
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
openapi:
	poetry run python task_management_system/manage.py spectacular --file $(docs)/openapi.yaml

# Generate Certificats for Lets Encrypt
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
poetry:
	pipx install poetry==$(poetry-version)

# Install pre-commit
pre-commit:
	poetry install
	poetry run pre-commit install


#
# Infrastructure commands
#

# Create backend
create-backend:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-admin)
	./infrastructure/scripts/bootstrap create

destroy-backend:
	./infrastructure/scripts/bootstrap destroy

# Development infrastructure
#

# Create AMI gitlab-runner image
create-runner-img:
	cd $(packer-runner-dir)
	export AWS_PROFILE=$(aws-user-admin)
	packer init .
	packer build gitlab-runner.pkr.hcl

# Create development network
create-network-dev:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/network install dev

# Update development network
update-network-dev:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/network update dev

# Destroy development network
destroy-network-dev:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/network destroy dev

# Create development ssm-transfer-bucket
create-ssm-transfer-bucket-dev:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/ssm-transfer install dev

# Update development ssm-transfer-bucket
update-ssm-transfer-bucket-dev:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/ssm-transfer update dev

# Destroy development ssm-transfer-bucket
destroy-ssm-transfer-bucket-dev:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/ssm-transfer destroy dev


# Commands to install or destroy a gitlab-runner
install-gitlab-runner:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/gitlab-runner install

# Commands to install or destroy a gitlab-runner
update-gitlab-runner:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/gitlab-runner update

# Commands to destroy gitlab-runner
destroy-gitlab-runner:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-dev)
	./infrastructure/scripts/gitlab-runner destroy

# Production infrastructure
#

# Create AMI kube-node image
create-node-img:
	cd $(packer-node-dir)
	export AWS_PROFILE=$(aws-user-prod-packer)
	packer init .
	packer build kube-node.pkr.hcl

# Create production network
create-network-prod:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-prod-network)
	./infrastructure/scripts/prod/network install

# Update production network
update-network-prod:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-prod-network)
	./infrastructure/scripts/prod/network update

# Destroy production network
destroy-network-prod:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-prod-network)
	./infrastructure/scripts/prod/network destroy

# Create production kube environment
create-kube-prod:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-prod-kube)
	./infrastructure/scripts/prod/kube install

# Update production kube environment
update-kube-prod:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-prod-kube)
	./infrastructure/scripts/prod/kube update

# Destroy production kube environment
destroy-kube-prod:
	export TF_VAR_account_id=$(owner_id)
	export AWS_PROFILE=$(aws-user-prod-kube)
	./infrastructure/scripts/prod/kube destroy
