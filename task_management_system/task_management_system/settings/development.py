from __future__ import annotations

from os import environ

from task_management_system.core.logging import TmsLogger
from task_management_system.settings.base import *  # noqa F403

DEBUG = True

SECRET_KEY = environ.get("SECRET_KEY", "very-secret-development-key07123")

ALLOWED_HOSTS: list[str] = environ.get(
    "DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1 0.0.0.0"
).split(" ")

DATABASES = {
    "default": {
        "ENGINE": environ.get("SQL_ENGINE", "django.db.backends.postgresql"),
        "NAME": environ.get("SQL_DB", "postgres-dev"),
        "USER": environ.get("SQL_USER", "postgres"),
        "PASSWORD": environ.get("SQL_PASSWORD", "postgres"),
        "HOST": environ.get("SQL_HOST", "db-dev"),
        "PORT": environ.get("SQL_PORT", "5432"),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = environ.get("EMAIL_HOST")
EMAIL_PORT = environ.get("EMAIL_PORT")
EMAIL_HOST_USER = environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

TmsLogger("DEBUG")
