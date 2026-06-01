from __future__ import annotations

from os import environ

from task_management_system.core.logging import TmsLogger
from task_management_system.settings.base import *  # noqa F403
from task_management_system.settings.base import BASE_DIR

DEBUG = False
SECRET_KEY = environ["SECRET_KEY"]
ALLOWED_HOSTS = environ["DJANGO_ALLOWED_HOSTS"].split(" ")

DATABASES = {
    "default": {
        "ENGINE": environ.get("SQL_ENGINE", "django.db.backends.postgresql"),
        "NAME": environ["SQL_DB"],
        "USER": environ["SQL_USER"],
        "PASSWORD": environ["SQL_PASSWORD"],
        "HOST": environ["SQL_HOST"],
        "PORT": environ.get("SQL_PORT", "5432"),
    }
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Secure cookies — only needed, because admin site is still allowed.
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Nginx handles https checks
SILENCED_SYSTEM_CHECKS = ["security.W004", "security.W008"]

# We need this because of swagger ui
STATIC_ROOT = BASE_DIR / "staticfiles"

TmsLogger("INFO")
