FROM python:3.13-slim-bookworm AS build

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /app

RUN python -m pip install --no-cache-dir poetry==2.1.1 poetry-plugin-export==1.0.3 \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --without-hashes > requirements.txt

FROM python:3.13-alpine AS prod

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN addgroup -S tms && adduser -S tms -G tms
ENV TMS_HOME=/home/tms/web

WORKDIR $TMS_HOME

RUN apk add --no-cache \
    curl=8.19.0-r0 \
    netcat-openbsd=1.234.1-r0

COPY --from=build /app/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
COPY ./task_management_system/ ./

USER tms

ENTRYPOINT ["/home/tms/web/entrypoint"]
