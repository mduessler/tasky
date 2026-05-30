# Build image fror tasky production image
#
FROM python:3.13-slim-bookworm AS build

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /app

RUN python -m pip install --no-cache-dir poetry==2.1.1 poetry-plugin-export==1.0.3 \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

# Export python dependencies and keep hashes for integrity
RUN poetry export -f requirements.txt > requirements.txt

# Final image fror tasky production image
#
FROM python:3.13-alpine AS final

# Set Environmentvariables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TASKY_HOME=/home/tasky/web

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Creating user
RUN addgroup -S tasky && adduser -S tasky -G tasky --create-home

WORKDIR $TASKY_HOME

# Install os dependencies
RUN apk add --no-cache \
    curl=8.19.0-r0 \
    netcat-openbsd=1.234.1-r0

# Install python dependencies
COPY --from=build /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY  --chown=tasky:tasky ./task_management_system/ ./

# Change to non root-user
USER tasky

ENTRYPOINT ["/home/tasky/web/entrypoint"]
