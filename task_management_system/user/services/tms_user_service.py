from typing import Any

from django.core.exceptions import MultipleObjectsReturned, PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.db.models.deletion import ProtectedError
from loguru import logger
from rest_framework.exceptions import NotFound
from task.models import Task, TaskMembership, TaskNote
from user.errors import (
    PERMISSION_DENIED_TO_DELETE_USER,
    PERMISSION_DENIED_TO_UPDATE_USER,
    PERMISSION_DENIED_TO_VIEW_USER,
    PERMISSION_DENIED_TO_VIEW_USER_TASK_MEMBERSHIPS,
    PERMISSION_DENIED_TO_VIEW_USER_TASK_NOTES,
    PERMISSION_DENIED_TO_VIEW_USER_TASKS,
    USER_DOES_NOT_EXIST,
)
from user.models import TmsUser
from user.policies import TmsUserPolicy

from task_management_system.core.logging.utils import bind_context_dict


class TmsUserService:
    @staticmethod
    def get_user_via_id(actor: TmsUser, user_id: int) -> TmsUser:
        bind_context_dict(user=user_id)
        try:
            user = TmsUser.objects.get(id=user_id)
        except TmsUser.DoesNotExist:
            logger.warning("Not found: User does not exist.")
            raise NotFound(USER_DOES_NOT_EXIST)
        except MultipleObjectsReturned as exc:
            logger.critical(f"Critical: Multiple Users returned! Reason {exc}.")
            raise

        if not TmsUserPolicy.can_view(actor, user):
            logger.warning("Permission denied: Not allowed to view user.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_USER)

        logger.debug("Success: Found user.")
        return user

    @staticmethod
    def get_users(actor: TmsUser) -> QuerySet[TmsUser]:
        if not TmsUserPolicy.can_view_users(actor):
            logger.warning("Permission denied: Not allowed to view users.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_USER)
        logger.debug("Allowed: Returning users.")
        return TmsUser.objects.all()

    @classmethod
    def get_tasks_of_user(cls, actor: TmsUser, user_id: int) -> QuerySet[Task]:
        bind_context_dict(user=user_id)
        user = cls.get_user_via_id(actor, user_id)

        if not TmsUserPolicy.can_view_tasks_of_user(actor, user):
            logger.warning("Permission denied: Not allowed to view tasks of user.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_USER_TASKS)

        logger.debug("Allowed: Returning task of user.")
        return user.tasks.all()

    @classmethod
    def get_memberships_of_user(cls, actor: TmsUser, user_id: int) -> QuerySet[Task]:
        bind_context_dict(user=user_id)
        user = cls.get_user_via_id(actor, user_id)

        if not TmsUserPolicy.can_view_memberships_of_user(actor, user):
            logger.warning("Permission denied: Not allowed to view task memberships of user.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_USER_TASK_MEMBERSHIPS)

        logger.debug("Allowed: Returning task membership of user.")
        return TaskMembership.objects.filter(user=user)

    @classmethod
    def get_notes_of_user(cls, actor: TmsUser, user_id: int) -> QuerySet[Task]:
        bind_context_dict(user=user_id)
        user = cls.get_user_via_id(actor, user_id)

        if not TmsUserPolicy.can_view_notes_of_user(actor, user):
            logger.warning("Permission denied: Not allowed to view task notes of user.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_USER_TASK_NOTES)

        logger.debug("Allowed: Returning task note of user.")
        return TaskNote.objects.filter(author=user)

    @classmethod
    @transaction.atomic  # type: ignore[misc]
    def delete(cls, actor: TmsUser, user_id: int) -> None:
        bind_context_dict(user=user_id)
        user = cls.get_user_via_id(actor, user_id)

        if not TmsUserPolicy.can_delete(actor, user):
            logger.warning("Permission denied: Not allowed to delete user.")
            raise PermissionDenied(PERMISSION_DENIED_TO_DELETE_USER)
        try:
            user.delete()
            logger.debug("Success: User deleted.")
        except ProtectedError:
            logger.error("Protected error: User deletion failed.")
            raise ValidationError("User cannot be deleted because it is still referenced")

    @classmethod
    @transaction.atomic  # type: ignore[misc]
    def update(cls, actor: TmsUser, user_id: int, validated_data: dict[str, Any]) -> TmsUser:
        bind_context_dict(user=user_id)
        user = cls.get_user_via_id(actor, user_id)

        requested_fields = set(validated_data.keys())
        fields = list(requested_fields)
        logger.debug(f"Updating fields: {requested_fields}.")

        if not TmsUserPolicy.can_update(actor, user, requested_fields):
            logger.warning("Permission denied: Not allowed to update fields.")
            raise PermissionDenied(PERMISSION_DENIED_TO_UPDATE_USER)

        if "password" in validated_data:
            logger.debug("Updating password.")
            password = validated_data.pop("password")
            user.set_password(password)

        for key, value in validated_data.items():
            setattr(user, key, value)

        try:
            user.full_clean()
            if fields:
                user.save(update_fields=fields)
        except (ValidationError, IntegrityError) as exc:
            logger.warning(f"Validation error: can not update user. Reason: {exc}")
            raise

        logger.debug("Success: User updated.")
        return user
