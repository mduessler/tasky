# CI/CD Pipeline

## Overview

The pipeline runs automatically on pushes to `dev` and `main`. It builds the
CI image, enforces code quality and OpenAPI schema consistency, runs the test
suite in parallel across all apps, scans dependencies for known CVEs, builds
the production images, and finally scans those images for vulnerabilities.

All jobs run on a self-hosted GitLab Runner provisioned on AWS — see
[infrastructure.md](./infrastructure.md#gitlab-runner) for the runner setup.

## Pipeline Structure

### Stages

The pipeline is divided into six stages that run sequentially:

| Stage          | Description                                                         |
| -------------- | ------------------------------------------------------------------- |
| `build-dev`    | Build and push the CI image used by all downstream jobs             |
| `lint`         | Run pre-commit hooks and validate the committed OpenAPI schema      |
| `test`         | Run the test suite in parallel, one job per app                     |
| `security-dev` | Scan Python dependencies for known CVEs (`pip-audit`)               |
| `build`        | Build and push the production application image and the nginx image |
| `security`     | Scan the production images with Trivy                               |

### Job Graph

Jobs are wired via `needs` rather than relying purely on stage order. This
gives each job a precise upstream dependency and allows independent jobs in
the same stage to run in parallel:

```text
build:dev-image
   ├── lint
   └── openapi
         └── test:registration
         └── test:task
         └── test:task_management_system
         └── test:tms_auth
         └── test:user
               └── pip-audit
                     ├── build:prod-image
                     └── build:prod-nginx-image
                           └── trivy
```

> The pipeline is effectively gated on `build:dev-image`. Since that job only
> runs on `dev` and `main`, the rest of the pipeline only runs there as well —
> no per-job `rules` block is needed.

### File Structure

The pipeline configuration is split across multiple files for readability.
`.gitlab-ci.yml` is the entry point and declares the stages, global variables,
and includes:

```text
.gitlab-ci.yml
.gitlab/ci/
├── build-jobs/
│   ├── dev/
│   │   └── image.yaml          # build:dev-image
│   └── prod/
│       ├── image.yaml          # build:prod-image
│       └── nginx-image.yaml    # build:prod-nginx-image
├── lint-jobs/
│   ├── lint.yaml               # lint
│   └── openapi.yaml            # openapi
├── test-jobs/
│   ├── base.yaml               # .test-base (shared config)
│   ├── registration.yaml
│   ├── task.yaml
│   ├── task_management_system.yaml
│   ├── tms_auth.yaml
│   └── user.yaml
└── security-jobs/
    ├── trivy.yaml              # .trivy-base (shared config)
    ├── dev/
    │   └── pip-audit.yaml      # pip-audit
    └── prod/
        └── trivy.yaml          # trivy
```

## Images

The pipeline uses four images, all based on Python 3.13.

### Dev Image

`dev/Dockerfile` — used for local development. Based on `python:3.13-slim-bookworm`.
Includes all dev dependencies, the application source, and the entrypoint script.
Not built by the pipeline.

### CI Image

`dev/Dockerfile.ci` — used by all pipeline jobs that need the Python environment
(lint, openapi, test, pip-audit). Based on `python:3.13-slim-bookworm`. Includes
all dev dependencies and the system tools required by the pre-commit hooks
(`git`, `curl`, `postgresql-client`, `hadolint`, `shfmt`, ...). Does not embed
the application source — GitLab checks out the repository into the job container
automatically.

### Prod Image

`prod/Dockerfile` — used for production deployments. Multi-stage build: the
build stage exports requirements via Poetry; the final stage is based on
`python:3.13-alpine`, installs only the runtime dependencies, runs as a
non-root user, and uses the entrypoint script.

### Prod Nginx Image

`prod/Dockerfile.nginx` — the reverse-proxy image fronting the application in
production. Built and scanned alongside the prod application image.

## Jobs

### build:dev-image

Builds the CI image from `dev/Dockerfile.ci` using Docker-in-Docker and pushes
it to the GitLab Container Registry with two tags: the commit short SHA and
`latest`. All subsequent jobs pull `$DEV_IMAGE_LATEST` as their job image.

This is the only job with an explicit `rules` block — it runs only on `dev`
and `main`. Every other job depends on it transitively via `needs`, so the
whole pipeline inherits that gating.

### lint

Runs all pre-commit hooks against the full repository (`pre-commit run --all-files`).
The hook set is the same one developers run locally — see
[Pre-commit](development.md#pre-commit) for the full list. Hook environments
are cached between pipeline runs (see [Caching](#caching)).

### openapi

validates that the committed `docs/openapi.yaml` matches the schema generated
from the current code. Regenerates the schema into a temp file, runs the same
`yamlfmt` hook against it that is applied to the committed version, then
`diff`s the two. The job fails on any real difference — formatting noise is
neutralized by running the same formatter on both sides.

Regenerate the committed schema locally with `make openapi`.

### test:\*

The test suite is split into five parallel jobs — one per app — to reduce
total pipeline runtime:

| Job                           | Tests                           |
| ----------------------------- | ------------------------------- |
| `test:registration`           | `tests/registration/`           |
| `test:task`                   | `tests/task/`                   |
| `test:task_management_system` | `tests/task_management_system/` |
| `test:tms_auth`               | `tests/tms_auth/`               |
| `test:user`                   | `tests/user/`                   |

All five jobs extend `.test-base`, which provides the shared configuration:

- Job image: `$DEV_IMAGE_LATEST`
- Service: `postgres:18.4-alpine`, available at host `postgres`
- Django settings, database credentials, JWT secret, and SMTP credentials
  injected as variables
- `before_script` waits for the database via `pg_isready`

______________________________________________________________________

The split is a runtime decision. The `task` app alone has over 1,000 tests
and takes roughly 1h 45m to run serially. Splitting the suite into five
parallel jobs — one per app — keeps the pipeline within an acceptable wall
time and lets each app's suite be retried independently when a job fails.

Each job runs in its own container with its own `postgres:18.4-alpine`
service instance, so the parallelism is safe: no shared database, no shared
filesystem, no cross-job state.

```shell
pytest tests/<app>/ -n <worker_cnt>
```

All test jobs depend on both `lint` and `openapi` — they only run if both
pass.

### pip-audit

Scans the installed Python dependencies in the CI image for known CVEs.
Runs after all test jobs pass. Fails on any reported vulnerability. This is
the dependency-side counterpart to the image-side Trivy scan that runs later.

### build:prod-image

Builds the production application image from `prod/Dockerfile` using
Docker-in-Docker and pushes it to the GitLab Container Registry with two
tags: the commit short SHA and `latest`. Runs after `pip-audit` succeeds.

### build:prod-nginx-image

Builds the production nginx image from `prod/Dockerfile.nginx` and pushes
it with the same tagging convention. Runs in parallel with
`build:prod-image`, both gated on `pip-audit`.

### trivy

Scans both production images with [Trivy](https://trivy.dev/) — both the
Dockerfiles (`trivy config`) and the built images (`trivy image`). Fails on
any `HIGH` or `CRITICAL` vulnerability and on any Dockerfile misconfiguration.

The Trivy vulnerability database is cached between runs via `.trivy-base`
(see [Caching](#caching)).

## Variables

### Global Variables

Defined in `.gitlab-ci.yml` and available to every job:

| Variable                  | Value                                                |
| ------------------------- | ---------------------------------------------------- |
| `DEV_IMAGE`               | `$CI_REGISTRY_IMAGE/dev:$CI_COMMIT_SHORT_SHA`        |
| `DEV_IMAGE_LATEST`        | `$CI_REGISTRY_IMAGE/dev:latest`                      |
| `PROD_IMAGE`              | `$CI_REGISTRY_IMAGE/prod:$CI_COMMIT_SHORT_SHA`       |
| `PROD_IMAGE_LATEST`       | `$CI_REGISTRY_IMAGE/prod:latest`                     |
| `PROD_NGINX_IMAGE`        | `$CI_REGISTRY_IMAGE/prod-nginx:$CI_COMMIT_SHORT_SHA` |
| `PROD_NGINX_IMAGE_LATEST` | `$CI_REGISTRY_IMAGE/prod-nginx:latest`               |

### Custom Variables

No custom CI/CD variables are required at this stage. The `.test-base`
configuration references `$SECRET_KEY`, `$JWT_SECRET_KEY`, `$email_host_user`,
and `$email_host_password`, but none of them need to be set for the current
pipeline to pass:

- `SECRET_KEY` falls back to a development default in `settings/development.py`.
- `JWT_SECRET_KEY` resolves to `None` — tolerated because the current test
  suite does not exercise paths that require a real signing key.
- `email_host_user` / `email_host_password` resolve to empty strings — Celery
  runs in eager mode during tests and does not open an SMTP connection.

These references will be replaced or made mandatory once the production
image (Milestone 3) is in place. See the
[milestones](https://gitlab.com/mduessler-group/tasky/-/milestones) for the
roadmap.

## Rules

`build:dev-image` runs only on pushes to `dev` and `main`:

```yaml
rules:
  - if: $CI_COMMIT_BRANCH == "dev"
  - if: $CI_COMMIT_BRANCH == "main"
```

Because every downstream job declares `build:dev-image` as a transitive
`needs` dependency, the entire pipeline runs only on those two branches.
Feature branches do not trigger the pipeline — quality checks on feature
branches are enforced locally via pre-commit, and any drift surfaces as soon
as the branch is merged into `dev`.

## Caching

Two caches are used to speed up pipeline runs:

| Job     | Cache                        | Path                 |
| ------- | ---------------------------- | -------------------- |
| `lint`  | Pre-commit hook environments | `.pre-commit-cache/` |
| `trivy` | Trivy vulnerability database | `.trivycache/`       |

The Trivy cache is defined in the `.trivy-base` hidden job and inherited by
the `trivy` job via `extends`.

## Runner

All jobs target the self-hosted GitLab Runner via the `dev` tag:

```yaml
tags:
  - dev
```

The runner is a hardened EC2 instance provisioned on AWS with Terraform,
Packer, and Ansible. The instance has no public IP and is reached only via
*AWS Systems Manager Session Manager*. See
[infrastructure.md](./infrastructure.md#gitlab-runner) for the full setup,
the AMI build, and the connection procedure.
