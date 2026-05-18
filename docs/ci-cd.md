# CI/CD Pipeline

## Overview

The pipeline runs automatically on pushes to `dev` and `main`. It builds the
development and production Docker images, enforces code quality via linting,
validates the OpenAPI schema, runs the test suite in parallel, performs security
scans on both the code and the production image, and finally builds and publishes
the production image to the GitLab Container Registry.

## Pipeline Structure

### Stages

The pipeline is divided into four stages that run sequentially:

| Stage      | Description                                               |
| ---------- | --------------------------------------------------------- |
| `build`    | Builds and pushes the dev image and the prod image        |
| `lint`     | Runs code quality checks and validates the OpenAPI schema |
| `test`     | Runs the test suite in parallel across all apps           |
| `security` | Scans Python dependencies and the production image        |

### File Structure

The pipeline configuration is split across multiple files for readability:

```
.gitlab-ci.yml               # Entry point: stages, global variables, includes
.gitlab/ci/
  build-jobs/
    dev-image.yaml           # build-dev-image job
    prod-image.yaml          # build-prod-image job
  lint-jobs/
    lint.yaml                # lint job
    openapi.yaml             # openapi job
  test-jobs/
    base.yaml                # .test-base hidden job (shared config)
    registration.yaml        # test-registration job
    task.yaml                # test-task job
    task_management_system.yaml
    tms_auth.yaml
    user.yaml
  security-jobs/
    pip-audit.yaml           # security job
    trivy.yaml               # scan-prod-image job
```

## Images

### Dev Image

`dev/Dockerfile` — used for local development. Based on `python:3.13-slim-bookworm`.
Includes all dev dependencies, the application source code, and an entrypoint
that waits for the database before starting the server.

### CI Image

`dev/Dockerfile.ci` — used by all pipeline jobs except the build jobs. Based on
`python:3.13-slim-bookworm`. Includes all dev dependencies and the tools required
by pre-commit hooks (`git`, `curl`, `ruby`, `ruby-dev`, `postgresql-client`,
`hadolint`, `shfmt`). Does not include the application source code or an entrypoint
— GitLab checks out the repository into the job container automatically.

### Prod Image

`prod/Dockerfile` — used for production deployments. Based on `python:3.13-alpine`.
Includes only production dependencies (no dev extras). Significantly smaller than
the dev image.

## Jobs

### build-dev-image

Builds the CI image from `dev/Dockerfile.ci` and pushes it to the GitLab Container
Registry with two tags: the commit SHA and `latest`.

This job runs first and all subsequent jobs depend on it via `needs`.

### lint

Runs all pre-commit hooks against the full repository using:

```shell
pre-commit run --all-files
```

The following hooks are enforced in the pipeline (see [Pre-commit](development.md#pre-commit)
for the full list):

| Hook           | Description                         |
| -------------- | ----------------------------------- |
| `black`        | Code formatting                     |
| `isort`        | Import sorting                      |
| `flake8`       | Linting                             |
| `mypy`         | Static type checking (strict mode)  |
| `bandit`       | Security linting                    |
| `hadolint`     | Dockerfile linting                  |
| `yamlfmt`      | YAML formatting                     |
| `markdownlint` | Markdown linting                    |
| `shfmt`        | Shell script formatting             |
| `bashate`      | Shell script linting                |
| `poetry-check` | Validates `pyproject.toml`          |
| `poetry-lock`  | Ensures `poetry.lock` is up to date |

Pre-commit environments are cached between pipeline runs to avoid reinstalling
hooks on every run.

### openapi

Validates that the committed `docs/openapi.yaml` is up to date by regenerating
the schema and comparing it against the committed version:

```shell
python manage.py spectacular --file docs/openapi.tmp.yaml
pre-commit run yamlfmt --files docs/openapi.tmp.yaml
diff docs/openapi.yaml docs/openapi.tmp.yaml
```

The job fails if the committed schema differs from the generated one. To update
the schema locally run:

```shell
make openapi
```

### Tests

The test suite is split into five parallel jobs — one per app — to reduce total
pipeline runtime:

| Job                           | Tests                           |
| ----------------------------- | ------------------------------- |
| `test-registration`           | `tests/registration/`           |
| `test-task`                   | `tests/task/`                   |
| `test-task-management-system` | `tests/task_management_system/` |
| `test-tms-auth`               | `tests/tms_auth/`               |
| `test-user`                   | `tests/user/`                   |

Each job:

- Starts a `postgres:18.4-alpine` service
- Waits for the database to be ready via `pg_isready`
- Runs pytest with `-n auto` to parallelize across all available CPUs

The `test-registration` job additionally starts a `redis:alpine` service for
Celery task testing.

All test jobs depend on both `lint` and `openapi` via `needs` — they only run
if both pass.

### security

Scans Python dependencies for known CVEs using
[pip-audit](https://pypi.org/project/pip-audit/):

```shell
pip-audit
```

The job runs after all test jobs have passed.

### build-prod-image

Builds the production image from `prod/Dockerfile` and pushes it to the GitLab
Container Registry with two tags: the commit SHA and `latest`.

This job runs after `security` passes — it is the last job to run in the pipeline
and only executes if the entire pipeline up to that point was successful.

### scan-prod-image

Scans the production image for known vulnerabilities using
[Trivy](https://trivy.dev/):

```shell
trivy config prod/Dockerfile
trivy image --exit-code 1 --severity HIGH,CRITICAL $PROD_IMAGE_LATEST
```

The job fails if any `HIGH` or `CRITICAL` vulnerabilities are found. Trivy also
scans the `prod/Dockerfile` for misconfigurations.

The Trivy vulnerability database is cached between pipeline runs.

