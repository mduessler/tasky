from typing import Any

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from tms_auth.errors import (
    PERMISSION_DENIED_TO_CREATE_USER,
    PERMISSION_DENIED_TO_DELETE_USER,
    PERMISSION_DENIED_TO_UPDATE_USER,
    PERMISSION_DENIED_TO_VIEW_USER,
)
from tms_auth.policies import TmsUserPolicy
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


class TmsUserService:
    @staticmethod
    def bind_log_context(**kwargs: Any) -> Any:
        return bind_context_dict(**kwargs)

    @staticmethod
    def get_user(actor: TmsUser, user_id: int) -> TmsUser:
        context = {"actor_id": actor.id, "user_id": user_id}
        log = TmsUserService.bind_log_context(**context)

        try:
            user = TmsUser.objects.get(pk=user_id)
        except TmsUser.DoesNotExist:
            log.warning("Not found: User not found.")
            raise

        if not TmsUserPolicy.can_view(actor, user):
            log.warning("Permission denied: Not allowed to view user.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_USER)

        log.debug("Permission granted: Actor can get the user.")
        return user

    @staticmethod
    def create(actor: TmsUser, validated_data: dict[str, Any]) -> TmsUser:
        context = {"actor_id": actor.id}
        log = TmsUserService.bind_log_context(**context)

        if not TmsUserPolicy.can_create(actor):
            log.warning("Permission denied: Not allowed to create user.")
            raise PermissionDenied(PERMISSION_DENIED_TO_CREATE_USER)

        try:
            user = TmsUser.objects.create_user(**validated_data)
            log.debug("Success: Actor created new user.")
            return user
        except (ValidationError, IntegrityError) as exc:
            log.error(f"Error: Failed to create user. {str(exc)}")
            raise ValidationError("Could not create user due to data integrity issues.")

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def delete(actor: TmsUser, user: TmsUser) -> None:
        context = {"actor_id": actor.id, "user_id": user.id}
        log = TmsUserService.bind_log_context(**context)

        if not TmsUserPolicy.can_delete(actor, user):
            log.warning("Permission denied: Not allowed to delete user.")
            raise PermissionDenied(PERMISSION_DENIED_TO_DELETE_USER)

        try:
            user.delete()
        except ProtectedError as exc:
            log.error(f"Protected error: Task deletion failed. {str(exc)}")
            raise ValidationError("Task cannot be deleted because it is still referenced")
        log.info("Success: User deleted.")

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def update(actor: TmsUser, user_id: int, validated_data: dict[str, Any]) -> TmsUser:
        user = TmsUserService.get_user(actor, user_id)

        context = {"actor_id": actor.id, "user_id": user_id}
        log = TmsUserService.bind_log_context(**context)

        requested_fields = set(validated_data.keys())
        if not TmsUserPolicy.can_update(actor, user, requested_fields):
            log.warning(f"Permission denied: Not allowed to update fields {requested_fields}")
            raise PermissionDenied(PERMISSION_DENIED_TO_UPDATE_USER)

        try:
            password = validated_data.pop("password", None)
            if password:
                user.set_password(password)

            for attr, value in validated_data.items():
                setattr(user, attr, value)

            user.save()
            log.info("Success: User updated.")
            return user
        except (ValidationError, IntegrityError) as exc:
            log.error(f"Error: Failed to update user. {str(exc)}")
            raise ValidationError("Could not update user.")
