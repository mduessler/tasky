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
