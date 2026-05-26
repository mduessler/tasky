# Tasky

A collaborative task management REST API built with Django REST Framework,
designed as a full-stack engineering exercise that spans application code,
self-managed CI/CD infrastructure, and Infrastructure-as-Code provisioning on
AWS. Built in the open, with a public roadmap toward a Kubernetes-based
production deployment.

> **Primary repository:** [gitlab.com/mduessler-group/tasky](https://gitlab.com/mduessler-group/tasky)
> This GitHub repository is an automatic mirror. All development — CI/CD
> pipelines, issues, milestones, merge requests — happens on GitLab.

## Project Status

Tasky is built in the open. Each milestone is scoped as a set of GitLab issues
and ships through the CI/CD pipeline in this repository.

### Shipped

- REST API for users, tasks, memberships, and notes with versioning, JWT auth,
  and per-endpoint throttling
- **Layered application architecture.** Each app (`user`, `task`, `registration`,
  `tms_auth`) separates view, service, policy, and model concerns. Business rules
  live in services, authorization decisions live in policies, DRF permission classes
  consume policies. No fat views, no fat models.
- **Two access-control paradigms in one codebase.** Tasks use RBAC (owner / member
  roles assigned through `TaskMembership`). User-to-user visibility uses ReBAC
  (a user is visible to another user only via a shared task membership).
- **Email-verification registration flow** backed by Celery + Redis, with scheduled
  cleanup of expired tokens via Celery Beat.
- **Comprehensive test suite** — 213 test files executed in parallel across all
  apps in CI, with factories, fixtures, time-freezing, and timing-marker separation.
- **Six-stage CI/CD pipeline** with linting, OpenAPI schema validation, dependency
  vulnerability scanning, image building, and image vulnerability scanning. Only
  `build:dev-image` has explicit branch rules — every downstream job inherits the
  gating via `needs`. Clean pattern, no per-job `rules` duplication.
- **OpenAPI drift detection in CI.** The pipeline regenerates the OpenAPI schema,
  runs the same formatter the committed file was formatted with, and diffs the two.
  Catches drift between code and schema without failing on formatting noise.
- **Self-hosted GitLab Runner on AWS** — hardened AMI built with Packer (Docker
  and the GitLab Runner binary pre-installed), provisioned with Terraform, configured
  and registered with Ansible at boot. The running instance has no public IP, no
  inbound SSH — connection happens through SSM Session Manager.
- **Bootstrap-vs-environment split in Terraform.** A separate root module provisions
  the state backend (S3 + DynamoDB lock + access logging) before any environment
  module runs. Two AWS profiles enforce least privilege between bootstrap and runtime
  operations.

### Milestones

**Current focus — Milestone 3:** Production AWS infrastructure.

**Roadmap** ([all milestones on GitLab](https://gitlab.com/mduessler-group/tasky/-/milestones))

| Milestone | Scope                         |
| --------- | ----------------------------- |
| M3        | Production AWS infrastructure |
| M4        | Kubernetes deployment         |
| M5        | Production deployment         |
| M6        | Validation & release          |

## Tech Stack

### Application

- [**Django**](https://www.djangoproject.com/) + [**DRF**](https://www.django-rest-framework.org/)\
  Application framework and REST layer.
- [**djangorestframework-simplejwt**](https://github.com/jazzband/djangorestframework-simplejwt)\
  JWT authentication.
- [**PostgreSQL**](https://www.postgresql.org/)\
  Relational storage.
- [**Celery**](https://docs.celeryq.dev/) + [**Redis**](https://redis.io/)\
  Async task queue and broker.
- [**django-celery-beat**](https://django-celery-beat.readthedocs.io/)\
  Database-backed periodic task scheduler.
- [**nginx**](https://nginx.org/)\
  Reverse proxy and HTTPS termination.
- [**Loguru**](https://github.com/Delgan/loguru)\
  Structured logging.
- [**drf-spectacular**](https://drf-spectacular.readthedocs.io/)\
  OpenAPI schema and Swagger UI.

### Infrastructure

- [**Terraform**](https://developer.hashicorp.com/terraform)\
  Provisioning (state backend + GitLab Runner environment).
- [**Packer**](https://developer.hashicorp.com/packer)\
  Hardened AMI for the GitLab Runner (Docker + Runner baked in).
- [**Ansible**](https://docs.ansible.com/)\
  Runner configuration and registration.
- [**AWS**](https://aws.amazon.com/) (EC2, S3, DynamoDB, IAM, SSM)\
  Cloud platform.

### Build & CI

- [**Docker**](https://www.docker.com/) + Compose\
  Containerized dev environment and CI/prod runtime.
- [**GitLab CI/CD**](https://docs.gitlab.com/ee/ci/)\
  Pipeline orchestration.
- [**pytest**](https://docs.pytest.org/) + xdist + factory-boy\
  Test runner, parallelization, fixtures.
- [**Trivy**](https://trivy.dev/) + [**pip-audit**](https://github.com/pypa/pip-audit)\
  Image and dependency vulnerability scanning.
- [**Poetry**](https://python-poetry.org/)\
  Dependency management.

## Documentation

- [Architecture](docs/architecture.md) — Data model, authentication, permissions, registration flow
- [Development](docs/development.md) — Setup, environment variables, testing, logging

## Repository Layout

```text
tasky/
├── task_management_system/        # Django project root
│   ├── task_management_system/    # Settings, URL conf, celery app
│   ├── user/                      # Custom user model
│   ├── tms_auth/                  # JWT auth (login, logout, refresh)
│   ├── registration/              # Email-verification signup flow
│   ├── task/                      # Tasks, memberships, notes
│   └── tests/                     # Test suite (per-app subdirectories)
├── dev/                           # Dev Dockerfile, compose, nginx config
├── prod/                          # Production Dockerfile + nginx
├── infrastructure/
│   ├── terraform/
│   │   ├── bootstrap/             # State backend (S3 + DynamoDB + logs)
│   │   └── environment/dev/       # GitLab Runner environment
│   ├── packer/                    # Runner AMI build
│   ├── ansible/                   # Runner configuration
│   └── scripts/                   # Orchestration wrappers
├── .gitlab/ci/                    # Pipeline job definitions
└── docs/                          # Architecture, dev, infra, CI/CD
```

## Quickstart

**Prerequisites:** Docker, Docker Compose, Make

Just run the following command from the root, to run the development environment
If no .env file is specified, for the development environment, a file with
random values is generated from .env.example. The exceptions are *EMAIL_HOST_USER*
and *EMAIL_HOST_PASSWORD*. These values must always be set manually. However, they
are only needed when a user is to be registered.

```shell
make first-run   # 
```

The API is then available at:

- `https://localhost:8443/api/` — REST API
- `https://localhost:8443/api/docs/` — Swagger UI

> The browser will show a security warning for the self-signed certificate.
> This is expected — click "Advanced" and proceed.

See [docs/development.md](docs/development.md) for the full set of Make
targets (testing, seeding, security scans, OpenAPI regeneration).

## License

MIT — see [LICENSE](LICENSE).
