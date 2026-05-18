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

