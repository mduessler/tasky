# Build image fror tasky production image
#
FROM python:3.13-slim-bookworm AS build

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /app

RUN python -m pip install --no-cache-dir poetry==2.1.1 poetry-plugin-export==1.10.0 \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

# Export python dependencies and keep hashes for integrity
RUN poetry export -f requirements.txt > requirements.txt

# Final image fror tasky production image
#
FROM python:3.13-alpine@sha256:420cd0bf0f3998275875e02ecd5808168cf0843cbb4d3c536432f729247b2acc AS final

# Set Environmentvariables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TASKY_HOME=/home/tasky/web

# Creating user
RUN addgroup -S tasky && adduser -S tasky -G tasky

# Install os dependencies
RUN apk add --no-cache \
    curl \
    netcat-openbsd

# Create root directory of app and set owner
RUN mkdir -p "$TASKY_HOME" && chown -R tasky:tasky /home/tasky/web
WORKDIR $TASKY_HOME


# Install python dependencies
COPY --from=build /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY  --chown=tasky:tasky ./task_management_system/ ./

# Change to non root-user
USER tasky

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/healthz/ || exit 1

ENTRYPOINT ["/home/tasky/web/entrypoint"]
