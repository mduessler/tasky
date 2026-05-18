# Tasky

A task management REST API built with Django REST Framework. Tasky allows users
to create and manage tasks collaboratively, with a role-based permission system
and JWT authentication.

## Tech Stack

- [**Django**](https://www.djangoproject.com/)\
  Web framework used as the foundation of the application.
- [**Django REST Framework**](https://www.django-rest-framework.org/)\
  REST API layer built on top of Django.
- [**djangorestframework-simplejwt**](https://github.com/jazzband/djangorestframework-simplejwt)\
  JWT authentication for the REST API.
- [**PostgreSQL**](https://www.postgresql.org/)\
  Relational database used for persistent storage.
- [**Celery**](https://docs.celeryq.dev/)\
  Asynchronous task queue used for email sending and periodic cleanup.
- [**Redis**](https://redis.io/)\
  Message broker for Celery.
- [**nginx**](https://nginx.org/)\
  Reverse proxy that handles HTTPS termination and forwards requests to the application.
- [**Docker**](https://www.docker.com/)\
  Container runtime used to run services consistently across environments.
- [**drf-spectacular**](https://drf-spectacular.readthedocs.io/)\
  OpenAPI schema generation and Swagger UI.

## Quickstart

**Prerequisites:** Docker, Docker Compose, Make

```shell
# Generate a self-signed SSL certificate (first time only)
make gen-cert-dev

# Start the development stack
make run-dev
```

The API is now available at `https://localhost:8443/api/` and the Swagger UI
at `https://localhost:8443/api/docs/`.

> The browser will show a security warning for the self-signed certificate —
> this is expected. Click "Advanced" and proceed.

## Documentation

- [Architecture](docs/architecture.md) — Data model, authentication, permissions, registration flow
- [Development](docs/development.md) — Setup, environment variables, testing, logging
