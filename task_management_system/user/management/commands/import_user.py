from json import load
from typing import Any

from django.core.management.base import BaseCommand
from django.db import connection
from user.models import TmsUser

from task_management_system.utils import TEST_DATA

USERS = TEST_DATA / "auth" / "user.json"


class Command(BaseCommand):  # type: ignore[misc]
    def handle(self, *args: Any, **options: Any) -> None:
        with open(USERS, "r") as f:
            users = load(f)
            for user in users:
                if TmsUser.objects.filter(email=user["email"]).exists():
                    continue
                if user["is_staff"]:
                    TmsUser.objects.create_superuser(**user)
                else:
                    TmsUser.objects.create_user(**user)

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT setval(pg_get_serial_sequence('user_tmsuser', 'id'), "
                    "MAX(id)) FROM user_tmsuser"
                )
