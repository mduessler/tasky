# Development

- [Getting Started](#getting-started)
- [Development Process Overview](#development-process-overview)
  - [Branch Structure](#branch-structure)
  - [Development Workflow](#development-workflow)
    - [1. Issue Creation](#1-issue-creation)
    - [2. Feature Development](#2-feature-development)
    - [3. Merging into dev](#3-merging-into-dev)
    - [4. Release to main](#4-release-to-main)
  - [Hotfix Workflow (Special Case)](#hotfix-workflow-special-case)
- [Dev Dependencies](#dev-dependencies)
- [Makefile Commands](#makefile-commands)
- [Environment Variables](#environment-variables)
- [Pre-commit](#pre-commit)
- [Testing](#testing)
  - [Configuration](#configuration)
  - [Markers](#markers)
  - [Factories & Fixtures](#factories--fixtures)
- [Celery](#celery)
  - [Tasks](#tasks)
- [Management Commands](#management-commands)
  - [`import_user`](#import_user)
  - [`clean_tokens`](#clean_tokens)
- [Logging](#logging)
  - [Directory Structure](#directory-structure)
  - [Context Storage](#context-storage)
  - [Other Variables](#other-variables)
- [OpenAPI schema generation with Django Spectacular](#openapi-schema-generation-with-django-spectacular)
  - [Explanation](#explanation)

## Prerequisites

The following tools must be installed on your machine before you can run the
development stack:

- **[Docker](https://www.docker.com/)**\
  Container runtime used to run services consistently across environments.
- **[Docker Compose](https://docs.docker.com/compose/)**\
  Tooling to orchestrate multi-service setups such as Neo4j and backend APIs.
- **[Make](https://www.gnu.org/software/make/)**\
  Task runner used to standardize common development and test commands.
- **[Poetry](https://python-poetry.org/)** (`2.2.1`)\
  Python packaging and dependency management.
  > Installation can be done with Make. Instructions listed below.
- **[pre-commit](https://pre-commit.com/)** (`4.6.0`)\
  Git hooks framework used to enforce code quality checks before commits.
  > Installation can be done with Make. Instructions listed below.
- **[Infrastructure](./infrastructure.md)**\
  The dependencies to install, modify or delete the infrastructure are defined
  in the documentation of the infrastructure.

## Getting Started

The development stack runs entirely in Docker. To start it, run:

```shell
make run-dev
```

This will:

1. Build and start all containers
2. Wait for the database to be ready
3. Run migrations
4. Import the default superuser
5. Clean expired tokens
6. Attach to the logs of all containers

The API is available at:

| URL                           | Description                                                  |
| ----------------------------- | ------------------------------------------------------------ |
| `https://localhost:8443/api/` | HTTPS — recommended, used for browser and Swagger UI         |
| `http://localhost:8080/api/`  | HTTP — only available in development for REST client testing |

> In production only HTTPS is available. Port 8080 is intentionally left
> unencrypted in development to simplify local API testing with tools like
> Bruno or rest.nvim that may not support self-signed certificates out of the box.

The Swagger UI is available at `https://localhost:8443/api/docs/`.

## Development Process

### Branches

Two long-lived branches:

- **`main`** — production-ready, protected, only updated via release merges from `dev` or hotfixes.
- **`dev`** — integration branch, protected, target for all feature work.

### Workflow

1. **Open an issue** describing the work (feature, bug, refactor, etc.).
2. **Create a branch from `dev`** named `<type>/<issue-id>-<short-description>`
   (e.g. `feature/142-token-cleanup`).
3. **Commit and push** regularly. Reference the issue ID in commit messages.
4. **Open a merge request into `dev`**. At least one approval is required before
   merging.
5. **Release**: once enough changes have accumulated on `dev`, it is merged into
   `main` and tagged following [SemVer](https://semver.org/).

### Hotfixes

Critical production issues bypass the normal cycle:

1. Branch from `main` as `hotfix/<issue-id>-<short-description>`.
2. Merge the fix into `main` and tag a patch release.
3. Merge `main` back into `dev` to keep the branches in sync.

## Make Commands

The `Makefile` provides shortcuts for the most common development, test and
infrastructure tasks. All commands are invoked from the repository root via
`make <target>`.

### Local Setup

| Command           | Description                                                 |
| ----------------- | ----------------------------------------------------------- |
| `make poetry`     | Install Poetry (version `2.2.1`) via `pipx`.                |
| `make pre-commit` | Install project dependencies and register pre-commit hooks. |

### Development Environment

| Command               | Description                                                                  |
| --------------------- | ---------------------------------------------------------------------------- |
| `make up-dev`         | Build and start all containers, wait for the database, clean expired tokens. |
| `make run-dev`        | Same as `up-dev` and additionally attach to the logs of all containers.      |
| `make stop-dev`       | Stop all running dev containers without removing them.                       |
| `make down-dev`       | Stop and remove dev containers (keeps images and volumes).                   |
| `make clean-dev`      | Stop and remove the application container and its image.                     |
| `make full-clean-dev` | Stop and remove all containers, images and the database volume.              |

### Database & Seed Data

| Command               | Description                                          |
| --------------------- | ---------------------------------------------------- |
| `make makemigrations` | Generate Django migrations for the project apps.     |
| `make seed-dev`       | Import the default superuser and load test fixtures. |

### Tests

Test targets are documented in the [Testing](#Testing) section.

### Generated Artifacts

| Command             | Description                                                         |
| ------------------- | ------------------------------------------------------------------- |
| `make openapi`      | Generate the OpenAPI specification at `docs/openapi.yaml`.          |
| `make gen-cert-dev` | Generate a self-signed certificate for local HTTPS in `dev/certs/`. |

### Infrastructure

| Command                      | Description                                                        |
| ---------------------------- | ------------------------------------------------------------------ |
| `make bootstrap-create`      | Create the Terraform backend (uses the `tasky-admin` AWS profile). |
| `make bootstrap-destroy`     | Destroy the Terraform backend.                                     |
| `make create-runner-img`     | Build the GitLab runner AMI with Packer.                           |
| `make install-gitlab-runner` | Provision a GitLab runner (uses the `tasky-dev` AWS profile).      |
| `make destroy-gitlab-runner` | Tear down the GitLab runner.                                       |

## Environment Variables

The development environment is configured via the `dev/.env.dev` file in the root
directory. Never commit this file to version control — use `.env.example` as
a reference instead.

| Variable                 | Description                                                       | Example                                       |
| ------------------------ | ----------------------------------------------------------------- | --------------------------------------------- |
| `DJANGO_SETTINGS_MODULE` | The settings module to use                                        | `task_management_system.settings.development` |
| `SECRET_KEY`             | Django's secret key, used for cryptographic signing               | `django-insecure-...`                         |
| `DJANGO_ALLOWED_HOSTS`   | Space-separated list of allowed hosts                             | `localhost 127.0.0.1 0.0.0.0`                 |
| `SQL_ENGINE`             | The database backend to use                                       | `django.db.backends.postgresql`               |
| `SQL_DB`                 | The name of the database                                          | `postgres-dev`                                |
| `SQL_USER`               | The database user                                                 | `postgres`                                    |
| `SQL_PASSWORD`           | The database password                                             | `postgres`                                    |
| `SQL_HOST`               | The database host — must match the service name in docker-compose | `db-dev`                                      |
| `SQL_PORT`               | The database port                                                 | `5432`                                        |
| `JWT_SECRET_KEY`         | The signing key used to sign and verify JWT tokens                | `a-very-strong-secret`                        |
| `EMAIL_HOST`             | The SMTP host                                                     | `sandbox.smtp.mailtrap.io`                    |
| `EMAIL_PORT`             | The SMTP port                                                     | `2525`                                        |
| `EMAIL_HOST_USER`        | The SMTP user                                                     | `<mailtrap-user>`                             |
| `EMAIL_HOST_PASSWORD`    | The SMTP password                                                 | `<mailtrap-password>`                         |

## Pre-commit

Pre-commit runs a set of hooks before every commit to ensure code quality and
consistency. If a hook fails, the commit is aborted; formatting hooks will
modify files in place, so you can simply `git add` the changes and commit again.

The following hooks are configured:

| Hook           | Description                         |
| -------------- | ----------------------------------- |
| `black`        | Code formatting                     |
| `isort`        | Import sorting                      |
| `flake8`       | Linting                             |
| `mypy`         | Static type checking (strict mode)  |
| `bandit`       | Security linting                    |
| `poetry-check` | Validates `pyproject.toml`          |
| `poetry-lock`  | Ensures `poetry.lock` is up to date |
| `yamlfmt`      | YAML formatting                     |
| `hadolint`     | Dockerfile linting                  |
| `shellcheck`   | Shell script linting                |
| `shfmt`        | Shell script formatting             |
| `markdownlint` | Markdown linting                    |
| `mdformat`     | Markdown formatting                 |

To install the hooks run:

```shell
make pre-commit
```

> The same hooks run in CI, so bypassing them locally with `--no-verify` will
> only delay the failure.

## Testing

Tests are run via pytest. The test suite is split into two groups:

| Command                  | Description                                                     |
| ------------------------ | --------------------------------------------------------------- |
| `make tests`             | Run unit tests and security tests in sequence.                  |
| `make unit-tests`        | Run pytest, excluding tests marked `timing`.                    |
| `make unit-tests-full`   | Run pytest including the `timing` suite.                        |
| `make security-tests`    | Build production images, run `pip-audit`, then scan with Trivy. |
| `make security-scan-dev` | Build the CI dev image and scan it with Trivy.                  |

> All tests are also executed in CI when a merge request targets a [long-lived branch](#branches).
> Failing tests block the pipeline and prevent merging.

### Configuration

The pytest configuration is defined in `pytest.ini`. Tests run in parallel
with 10 workers by default (`-n 10`).

### Markers

| Marker   | Description                                                                                  |
| -------- | -------------------------------------------------------------------------------------------- |
| `timing` | Timing side-channel tests for passphrase verification. Only run with `make unit-tests-full`. |
| `slow`   | Tests that take noticeably longer to run. Skip with `-m "not slow"`.                         |

### Factories & Fixtures

The test suite uses [**factory-boy**](https://factoryboy.readthedocs.io/) to generate
test data. Shared factories and fixtures are defined under `tests/fixtures/` and
are available across all tests. App-specific fixtures are defined in the respective
`conftest.py` files.

Each fixture also has a read-only counterpart suffixed with `_read_only`. These
use `scope="class"` so the underlying objects are created once per test class
instead of per test, reducing overall test runtime. Use them whenever a test
only reads from the fixture and does not modify its state.


## Celery

Celery handles asynchronous and scheduled tasks. The dev stack runs two
Celery services defined in `dev/docker-compose.yaml`:

| Service         | Description                           |
| --------------- | ------------------------------------- |
| `celery-worker` | Executes asynchronous tasks           |
| `celery-beat`   | Schedules and triggers periodic tasks |

Both services are started automatically via `make run-dev`.

### Tasks

| Task                           | Type     | Description                                                                                                                                               |
| ------------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `send_verification_email_task` | Async    | Sends the verification email after registration. Retries up to 5 times on `SMTPException`, `ConnectionError`, or `TimeoutError` with exponential backoff. |
| `cleanup_expired_tokens`       | Periodic | Deletes expired `EmailVerificationToken` entries. Runs every 60 seconds via Celery Beat.                                                                  |

## Management Commands

The following custom management commands are available:

### `import_user`

Creates a default superuser if no superuser exists yet. The command is
automatically run on `make up-dev`.

```shell
python manage.py import_user
```

### `clean_tokens`

Deletes all expired `EmailVerificationToken` entries from the database.
The command is automatically run on `make up-dev` and periodically by
Celery Beat every 60 seconds.

```shell
python manage.py clean_tokens
```

## Logging

This chapter outlines the architecture and implementation of the logging system
within the `task_mangement_system`. The system leverages the [loguru](https://github.com/delgan/loguru)
library to provide structured, context-aware logging across asynchronous requests
and multiple threads.

### Directory Structure

The logging implementation is centralized within the core of the application:
`task_mangement_system/task_mangement_system/core/logging/`.

- [**config.py**](../task_management_system/task_management_system/core/logging/config.py):
  Logger configuration, sink definitions, and interception.
- [**middleware.py**](../task_management_system/task_management_system/core/logging/middleware.py):
  Custom logging middleware for request tracking.
- [**utils.py**](../task_management_system/task_management_system/core/logging/config.py)
  Context storage and thread-local "extra" dictionary management.

### Context Storage

The context storage is used to store individual information for each request without
overriding the information of other requests.

To identify each request, the logging middleware stores a unique identifier for
each request. The request identifier is generated with the uuid4 function. It also
stores the user, path, and method used.

The values are represented by the following variables:

- **id**: Request identifier
- **actor**: Request user
- **path**: Requested path
- **method**: Request method

### Other Variables

This section defines the names of fixed object IDs to ensure consistent naming
conventions and unified logging across the entire system.

- **task**: Task identifier
- **user**: User, which is not the actor.
- **actor_membership**: Actor task membership for the task
- **membership**: Task membership identifier
- **note**: Task note identifier

______________________________________________________________________

## OpenAPI schema generation with Django Spectacular

We use Django Spectacular to generate the `openapi.yaml` specification for the API.

In most cases, the schema is generated automatically from the default serializer
configuration. However, if a custom serializer setup is used (for example different
serializers for request and response bodies), the schema must be explicitly attached
to the corresponding class or function using `@extend_schema`.

Example:

```python
@extend_schema(
    request=RegisterWriteSerializer,
    responses={201: RegisterReadSerializer},
    tags=["auth"],
)
```

### Explanation

- `request`\
  Defines the serializer used for the incoming request body.

- `responses`\
  Defines the serializer returned by the endpoint.\
  In this example, HTTP `201 Created` responses use `RegisterReadSerializer`.

- `tags`\
  Groups the endpoint in the generated OpenAPI documentation.\
  This is only required if the endpoint path is **not** located under the default
  API prefix (e.g. `api/v1/...`).
