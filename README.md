# Tasky

> **Primary repository:** [gitlab.com/mduessler-group/tasky](https://gitlab.com/mduessler-group/tasky)
> This GitHub repository is an automatic mirror. All development — CI/CD
> pipelines, issues, milestones, merge requests — happens on GitLab.

[![pipeline](https://gitlab.com/mduessler-group/tasky/badges/main/pipeline.svg)](https://gitlab.com/mduessler-group/tasky/-/pipelines)

A collaborative task management REST API built with Django REST Framework,
designed as a full-stack engineering exercise that spans application code,
self-managed CI/CD infrastructure, and Infrastructure-as-Code provisioning on
AWS. Built in the open, with a public roadmap toward a Kubernetes-based
production deployment.

## Project Status

Tasky is built in the open. Each milestone is scoped as a set of GitLab issues
and ships through the CI/CD pipeline in this repository.

**Shipped**

- REST API for users, tasks, task memberships, and task notes, with API
  versioning (`/api/v1/`), JWT authentication with token blacklisting on
  logout, and per-endpoint throttling
- Email-verification registration flow backed by Celery + Redis, with
  scheduled cleanup of expired tokens via Celery Beat
- Two complementary access-control models: Role-Based Access Control for
  task resources, Relationship-Based Access Control for user resources
- Layered application architecture: views → services → policies → models,
  with selectors for read paths and explicit permission classes per endpoint
- Comprehensive test suite (213 test files) executed in parallel across all
  apps in CI, with factories, fixtures, time-freezing, and timing-marker
  separation
- Six-stage CI/CD pipeline with linting, OpenAPI schema validation,
  dependency vulnerability scanning, image building, and image vulnerability
  scanning
- Self-hosted GitLab Runner on AWS — no public IP, accessed via SSM
  Session Manager, provisioned end-to-end with Terraform + Packer + Ansible
- Two-tier IAM model: an admin user for bootstrapping the Terraform backend,
  a least-privilege dev user for environment provisioning

**Current focus — Milestone 3:** Production AWS infrastructure.

**Roadmap** ([all milestones on GitLab](https://gitlab.com/mduessler-group/tasky/-/milestones))

| Milestone | Scope                         |
| --------- | ----------------------------- |
| M3        | Production AWS infrastructure |
| M4        | Kubernetes deployment         |
| M5        | Production deployment         |
| M6        | Validation & release          |

## Highlights

A few specific things this project demonstrates beyond a typical CRUD API:

- **Layered application architecture.** Each app (`user`, `task`,
  `registration`, `tms_auth`) separates view, service, policy, and model
  concerns. Business rules live in services; authorization decisions live in
  policies; DRF permission classes consume policies. No fat views, no fat
  models.
- **Two access-control paradigms in one codebase.** Tasks use RBAC
  (owner / member roles assigned through `TaskMembership`). User-to-user
  visibility uses ReBAC (a user is visible to another user only via a shared
  task membership).
- **Pipeline gated on dev image build.** Only `build:dev-image` has explicit
  branch rules — every downstream job inherits the gating via `needs`. Clean
  pattern, no per-job `rules` duplication.
- **Bootstrap-vs-environment split in Terraform.** A separate root module
  provisions the state backend (S3 + DynamoDB lock + access logging) before
  any environment module runs. Two AWS profiles enforce least privilege.
- **Hardened runner AMI.** Packer pre-installs Docker and the GitLab Runner
  binary; Ansible configures and registers the runner at boot. The running
  instance has no public IP, no inbound SSH — connection happens through SSM
  Session Manager.
- **OpenAPI drift detection in CI.** The pipeline regenerates the OpenAPI
  schema, runs the same formatter the committed file was formatted with, and
  diffs the two. Catches drift between code and schema without failing on
  formatting noise.

## Tech Stack

**Application**

| Tool                                                                                       | Purpose                              |
| ------------------------------------------------------------------------------------------ | ------------------------------------ |
| [Django](https://www.djangoproject.com/) + [DRF](https://www.django-rest-framework.org/)   | Application framework and REST layer |
| [djangorestframework-simplejwt](https://github.com/jazzband/djangorestframework-simplejwt) | JWT authentication                   |
| [PostgreSQL](https://www.postgresql.org/)                                                  | Relational storage                   |
| [nginx](https://nginx.org/)                                                                | Reverse proxy and HTTPS termination  |
| [Loguru](https://github.com/Delgan/loguru)                                                 | Structured logging                   |
| [drf-spectacular](https://drf-spectacular.readthedocs.io/)                                 | OpenAPI schema and Swagger UI        |

**Infrastructure**

| Tool                                                         | Purpose                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------- |
| [Terraform](https://developer.hashicorp.com/terraform)       | Provisioning (state backend + GitLab Runner environment)      |
| [Packer](https://developer.hashicorp.com/packer)             | Hardened AMI for the GitLab Runner (Docker + Runner baked in) |
| [Ansible](https://docs.ansible.com/)                         | Runner configuration and registration                         |
| [AWS](https://aws.amazon.com/) (EC2, S3, DynamoDB, IAM, SSM) | Cloud platform                                                |

**Build & CI**

| Tool                                                                         | Purpose                                           |
| ---------------------------------------------------------------------------- | ------------------------------------------------- |
| [Docker](https://www.docker.com/) + Compose                                  | Containerized dev environment and CI/prod runtime |
| [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)                               | Pipeline orchestration                            |
| [pytest](https://docs.pytest.org/) + xdist + factory-boy                     | Test runner, parallelization, fixtures            |
| [Trivy](https://trivy.dev/) + [pip-audit](https://github.com/pypa/pip-audit) | Image and dependency vulnerability scanning       |
| [Poetry](https://python-poetry.org/)                                         | Dependency management                             |

Strict pre-commit chain — including `mypy --strict`, `bandit`, `hadolint`,
and `shellcheck` — enforced locally and again in CI. See
[development.md](docs/development.md#pre-commit) for the full set.

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

```shell
make gen-cert-dev   # Generate a self-signed SSL certificate (first time only)
make run-dev        # Build and start the full development stack
```

On first run, a `.env` file is generated automatically with random
development secrets. Edit it to configure email delivery if needed.

The API is then available at:

- `https://localhost:8443/api/` — REST API
- `https://localhost:8443/api/docs/` — Swagger UI

> The browser will show a security warning for the self-signed certificate.
> This is expected — click "Advanced" and proceed.

See [docs/development.md](docs/development.md) for the full set of Make
targets (testing, seeding, security scans, OpenAPI regeneration).

## Documentation

- [Architecture](docs/architecture.md) — Data model, authentication,
  permission model (RBAC + ReBAC), registration flow, exception handling
- [Development](docs/development.md) — Local setup, branching workflow, Make
  targets, testing strategy, logging conventions
- [Infrastructure](docs/infrastructure.md) — AWS provisioning of the
  Terraform backend and the self-hosted GitLab Runner (Terraform / Packer /
  Ansible / SSM)
- [CI/CD](docs/ci-cd.md) — Pipeline stages, job graph, images, variables,
  caching, runner integration

## License

MIT — see [LICENSE](LICENSE).
