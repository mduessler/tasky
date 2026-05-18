from typing import Any

from django.db.transaction import atomic
from user.models import TmsUser


def update_user(user: TmsUser, user_to_update: TmsUser, validated_data: dict[str, Any]) -> TmsUser:
    if not user.is_staff:
        raise PermissionError(f"User {user} has not the permission to update user.")

    with atomic():
        if "password" in validated_data:
            password = validated_data.pop("password")

        for attr, value in validated_data.items():
            setattr(user_to_update, attr, value)

        user_to_update.set_password(password)
        user_to_update.save(using=user_to_update._db)
        return user_to_update
