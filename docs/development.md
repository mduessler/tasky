# Development

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Default Data](#default-data)
  - [Default Users](#default-users)
  - [Running the Seed](#running-the-seed)
  - [Trying the API](#trying-the-api)
- [Development Process](#development-process)
  - [Branches](#branches)
  - [Workflow](#workflow)
  - [Hotfixes](#hotfixes)
- [Make Commands](#make-commands)
  - [Local Setup](#local-setup)
  - [Development Environment](#development-environment)
  - [Database & Seed Data](#database--seed-data)
  - [Tests](#tests)
  - [Generated Artifacts](#generated-artifacts)
  - [Infrastructure](#infrastructure)
- [Environment Variables](#environment-variables)
- [Pre-commit](#pre-commit)
- [Testing](#testing)
  - [Configuration](#configuration)
  - [Markers](#markers)
  - [Factories & Fixtures](#factories--fixtures)
- [Celery](#celery)
  - [Tasks](#tasks)
- [Logging](#logging)
  - [Directory Structure](#directory-structure)
  - [Context Storage](#context-storage)
  - [Other Variables](#other-variables)
- [OpenAPI Schema](#openapi-schema)

## Prerequisites

The following tools must be installed on your machine before you can run the
development stack:

- **[Docker](https://www.docker.com/)**\
  Container runtime used to run services consistently across environments.
- **[Docker Compose](https://docs.docker.com/compose/)**\
  Tooling to orchestrate multi-service setup of dev environment.
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
3. Run migrations (via [entrypoint](task_management_system/entrypoint))
4. Clean expired tokens
5. Attach to the logs of all containers

The API is available at:

| URL                           | Description                                                  |
| ----------------------------- | ------------------------------------------------------------ |
| `https://localhost:8443/api/` | HTTPS — recommended, used for browser and Swagger UI         |
| `http://localhost:8080/api/`  | HTTP — only available in development for REST client testing |

> In production only HTTPS is available. Port 8080 is intentionally left
> unencrypted in development to simplify local API testing with tools like
> Bruno or rest.nvim that may not support self-signed certificates out of the box.

The Swagger UI is available at `https://localhost:8443/api/docs/`.

## Default Data

`make seed-dev` populates the development database with default users and
example tasks, memberships, and notes. It is the recommended starting point
for trying out the API locally — every endpoint can be exercised against the
seeded fixtures without manually creating users first.

### Default Users

Fourteen users are created. One of them is a superuser. For testing purposes,
using 2 users is sufficient. The login credentials for the 2 users are listed
below. Otherwise, the [`request.http`](./requests.http) file contains a request
for each API endpoint. These users only exists in the development environment.

| Email             | Password     | Role      |
| ----------------- | ------------ | --------- |
| max@example.com   | customXXXX1  | user      |
| jonas@example.com | customXXXX14 | superuser |

> These credentials exist only in the development environment. The seed
> command does not run against production settings.

### Running the Seed

`make seed-dev` requires the development stack to already be running — it
executes the seeding inside the running application container. Two equivalent
workflows are supported:

**Two terminals** (recommended — keeps container logs visible):

```shell
# Terminal 1 — start the stack and attach to logs
make run-dev

# Terminal 2 — seed once the stack is up
make seed-dev
```

**Single terminal:**

```shell
make up-dev      # starts the stack detached
make seed-dev    # seeds users and fixtures
make run-dev     # attaches to the logs of the already-running stack
```

> `make up-dev` and `make run-dev` are documented in
> [Make Commands → Development Environment](#development-environment).

### Trying the API

Example requests covering login, token refresh, and the main task endpoints
— using the default users above — are provided in
[`requests.http`](./requests.http). The file is compatible with the JetBrains
HTTP client, the [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
extension for VS Code, and [httpYac](https://httpyac.github.io/).

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

Infrastructure targets are documented in
[infrastructure.md](./infrastructure.md#How-to-run-all).

## Environment Variables

The development stack is configured via a `.env.dev` file in the project root.
**Never commit `.env*` to version control.** If no `.env*` exists, `make up-dev`
generates one from `docs/.env.example` with random secrets. The exceptions
are `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` — these must be set manually
if you want to test the email verification step of registration.

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
| `cleanup_expired_tokens`       | Periodic | Registers a task, which deletes all expired `EmailVerificationToken` and runs every 60 seconds via Celery Beat.                                           |

## Logging

This chapter outlines the architecture and implementation of the logging system
within the `task_management_system`. The system leverages the [loguru](https://github.com/delgan/loguru)
library to provide structured, context-aware logging across asynchronous requests
and multiple threads.

### Directory Structure

The logging implementation is centralized within the core of the application:
`task_management_system/task_management_system/core/logging/`.

- [**config.py**](../task_management_system/task_management_system/core/logging/config.py):
  Logger configuration, sink definitions, and interception.
- [**middleware.py**](../task_management_system/task_management_system/core/logging/middleware.py):
  Custom logging middleware for request tracking.
- [**utils.py**](../task_management_system/task_management_system/core/logging/utils.py)
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

## OpenAPI Schema

The `openapi.yaml` specification is generated with
[drf-spectacular](https://drf-spectacular.readthedocs.io/). In most cases the
schema is inferred from the default serializer setup. Use `@extend_schema` when
an endpoint deviates from this — for example, when request and response use
different serializers, or when the endpoint lives outside the default
`api/v1/...` prefix and needs an explicit `tags` entry.

```python
@extend_schema(
    request=RegisterWriteSerializer,
    responses={201: RegisterReadSerializer},
    tags=["auth"],
)
```

See the [drf-spectacular documentation](https://drf-spectacular.readthedocs.io/)
for the full set of options.
