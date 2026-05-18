from datetime import timedelta
from os import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_celery_beat",
    "user",
    "tms_auth",
    "registration",
    "task",
]

AUTH_USER_MODEL = "user.TmsUser"

AUTHENTICATION_BACKENDS = [
    "tms_auth.backends.TmsEmailBackend",
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "SIGNING_KEY": environ.get("JWT_SECRET_KEY"),
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
}


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "task_management_system.core.logging.middleware.RequestContextLogMiddleware",
]

ROOT_URLCONF = "task_management_system.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [],
        },
    },
]

WSGI_APPLICATION = "task_management_system.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

STATIC_URL = "static/"
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BEAT_SCHEDULE = {
    "cleanup-tokens-every-minute": {
        "task": "registration.tasks.cleanup_expired_tokens",
        "schedule": 60.0,
    },
}
CELERY_BEAT_SYNC_EVERY = 1

ACTIVATE_USER_THROTTLE = {"activate": "5/min", "register": "4/min"}

TMS_AUTH_THROTTLE = {
    "login_jwt": {"burst": "3/min", "sustained": "200/day"},
    "refresh_jwt": {"burst": "6/hour", "sustained": "144/day"},
    "logout_jwt": {"burst": "3/min", "sustained": "200/day"},
}

TMS_USER_THROTTLE = {
    "read": {"burst": "5/sec", "sustained": "2000/day"},
    "create": {"burst": "0/sec", "sustained": "0/day"},
    "delete": {"burst": "1/sec", "sustained": "100/day"},
    "update": {"burst": "2/sec", "sustained": "500/day"},
}

TASK_THROTTLE = {
    "read": {"burst": "10/sec", "sustained": "5000/day"},
    "create": {"burst": "2/sec", "sustained": "200/day"},
    "delete": {"burst": "1/sec", "sustained": "50/day"},
    "update": {"burst": "4/sec", "sustained": "1000/day"},
}

TASK_MEMBERSHIP = {
    "read": {"burst": "50/sec", "sustained": "5000/day"},
    "create": {"burst": "4/sec", "sustained": "400/day"},
    "delete": {"burst": "1/sec", "sustained": "200/day"},
    "update": {"burst": "4/sec", "sustained": "400/day"},
}

TASK_NOTE = {
    "read": {"burst": "100/sec", "sustained": "10000/day"},
    "create": {"burst": "2/sec", "sustained": "800/day"},
    "delete": {"burst": "4/sec", "sustained": "400/day"},
    "update": {"burst": "2/sec", "sustained": "800/day"},
}

THROTTLE = {
    "anon": "100/day",
    "user": "1000/day",
    "login_jwt_burst": TMS_AUTH_THROTTLE["login_jwt"]["burst"],
    "login_jwt_sustained": TMS_AUTH_THROTTLE["login_jwt"]["sustained"],
    "refresh_jwt_burst": TMS_AUTH_THROTTLE["refresh_jwt"]["burst"],
    "refresh_jwt_sustained": TMS_AUTH_THROTTLE["refresh_jwt"]["sustained"],
    "logout_jwt_burst": TMS_AUTH_THROTTLE["logout_jwt"]["burst"],
    "logout_jwt_sustained": TMS_AUTH_THROTTLE["logout_jwt"]["sustained"],
    "activate_user": ACTIVATE_USER_THROTTLE["activate"],
    "register_user": ACTIVATE_USER_THROTTLE["register"],
    "tms_user_read_burst": TMS_USER_THROTTLE["read"]["burst"],
    "tms_user_read_sustained": TMS_USER_THROTTLE["read"]["sustained"],
    "tms_user_create_burst": TMS_USER_THROTTLE["create"]["burst"],
    "tms_user_create_sustained": TMS_USER_THROTTLE["create"]["sustained"],
    "tms_user_delete_burst": TMS_USER_THROTTLE["delete"]["burst"],
    "tms_user_delete_sustained": TMS_USER_THROTTLE["delete"]["sustained"],
    "tms_user_update_burst": TMS_USER_THROTTLE["update"]["burst"],
    "tms_user_update_sustained": TMS_USER_THROTTLE["update"]["sustained"],
    "task_read_burst": TASK_THROTTLE["read"]["burst"],
    "task_read_sustained": TASK_THROTTLE["read"]["sustained"],
    "task_create_burst": TASK_THROTTLE["create"]["burst"],
    "task_create_sustained": TASK_THROTTLE["create"]["sustained"],
    "task_delete_burst": TASK_THROTTLE["delete"]["burst"],
    "task_delete_sustained": TASK_THROTTLE["delete"]["sustained"],
    "task_update_burst": TASK_THROTTLE["update"]["burst"],
    "task_update_sustained": TASK_THROTTLE["update"]["sustained"],
    "task_membership_read_burst": TASK_MEMBERSHIP["read"]["burst"],
    "task_membership_read_sustained": TASK_MEMBERSHIP["read"]["sustained"],
    "task_membership_create_burst": TASK_MEMBERSHIP["create"]["burst"],
    "task_membership_create_sustained": TASK_MEMBERSHIP["create"]["sustained"],
    "task_membership_delete_burst": TASK_MEMBERSHIP["delete"]["burst"],
    "task_membership_delete_sustained": TASK_MEMBERSHIP["delete"]["sustained"],
    "task_membership_update_burst": TASK_MEMBERSHIP["update"]["burst"],
    "task_membership_update_sustained": TASK_MEMBERSHIP["update"]["sustained"],
    "task_note_read_burst": TASK_NOTE["read"]["burst"],
    "task_note_read_sustained": TASK_NOTE["read"]["sustained"],
    "task_note_create_burst": TASK_NOTE["create"]["burst"],
    "task_note_create_sustained": TASK_NOTE["create"]["sustained"],
    "task_note_delete_burst": TASK_NOTE["delete"]["burst"],
    "task_note_delete_sustained": TASK_NOTE["delete"]["sustained"],
    "task_note_update_burst": TASK_NOTE["update"]["burst"],
    "task_note_update_sustained": TASK_NOTE["update"]["sustained"],
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "EXCEPTION_HANDLER": "task_management_system.core.exceptions.custom_exception_handler",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": THROTTLE,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Tasky API",
    "DESCRIPTION": "A collaborative task management REST API with JWT authentication.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
}
