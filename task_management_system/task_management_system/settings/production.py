from os import environ

from task_management_system.core.logging import TmsLogger
from task_management_system.settings.base import *  # noqa F403

DEBUG = False

SECRET_KEY = environ.get("SECRET_KEY")

TmsLogger("DEBUG")
