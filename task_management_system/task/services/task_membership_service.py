from typing import Any

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, QuerySet
from loguru import logger
from rest_framework.exceptions import NotFound
from task.errors import (
    PERMISSION_DENIED_TO_CREATE_TASK_MEMBERSHIP,
    PERMISSION_DENIED_TO_DELETE_TASK_MEMBERSHIP,
    PERMISSION_DENIED_TO_UPDATE_TASK_MEMBERSHIP,
    PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP,
    TASK_MEMBERSHIP_DOES_NOT_EXIST,
)
from task.models import Task, TaskMembership
from task.policies import TaskMembershipPolicy
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


class TaskMembershipService:
    @staticmethod
    def _get_membership(note_id: int, update: bool = False) -> Task:
        try:
            if update:
                return TaskMembership.objects.select_for_update().get(pk=note_id)
            else:
                return TaskMembership.objects.get(pk=note_id)
        except TaskMembership.DoesNotExist:
            logger.warning("Not found: Task membership not found.")
            raise NotFound(TASK_MEMBERSHIP_DOES_NOT_EXIST)

    @staticmethod
    def get_task_membership(actor: TmsUser, membership_id: int) -> TaskMembership:
        bind_context_dict(membership=membership_id)

        membership = TaskMembershipService._get_membership(membership_id)
        bind_context_dict(task=membership.task_id)

        if not TaskMembershipPolicy.can_view(actor, membership):
            logger.warning("Permission denied: Actor cannot view the task membership.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP)

        logger.debug("Permission granted: Actor can view this task membership.")
        return membership

    @staticmethod
    def get_task_memberships(actor: TmsUser) -> QuerySet[TaskMembership]:
        if not TaskMembershipPolicy.can_view_task_memberships(actor):
            logger.warning("Permission denied: Actor can not view all memberships.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP)

        logger.debug("Permission granted: Actor can view all memberships.")
        return TaskMembership.objects.all()

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def create(actor: TmsUser, validated_data: dict[str, Any]) -> TaskMembership:
        bind_context_dict(task=validated_data["task"].id)

        if not TaskMembershipPolicy.can_create(actor, validated_data.get("task")):
            logger.warning("Permission denied: Actor cannot create a membership for task.")
            raise PermissionDenied(PERMISSION_DENIED_TO_CREATE_TASK_MEMBERSHIP)

        try:
            membership = TaskMembership.objects.create(**validated_data)
            bind_context_dict(membership=membership.id)
        except (ValidationError, IntegrityError) as exc:
            logger.warning(f"Validation error: can not create task membership. Reason: {exc}")
            raise

        logger.debug("Success: Task membership created.")
        return membership

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def delete(actor: TmsUser, membership_id: int) -> None:
        bind_context_dict(membership=membership_id)

        membership = TaskMembershipService._get_membership(membership_id)
        bind_context_dict(task=membership.task_id)

        if not TaskMembershipPolicy.can_delete(actor, membership):
            logger.warning("Permission denied: Actor cannot delete the membership.")
            raise PermissionDenied(PERMISSION_DENIED_TO_DELETE_TASK_MEMBERSHIP)

        try:
            membership.delete()
            logger.debug("Success: Task membership deleted.")
        except ProtectedError:
            logger.error("Protected error: Task membership deletion failed.")
            raise ValidationError(PERMISSION_DENIED_TO_DELETE_TASK_MEMBERSHIP)

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def update(
        actor: TmsUser, membership_id: int, validated_data: dict[str, Any]
    ) -> TaskMembership:
        bind_context_dict(membership=membership_id)

        membership = TaskMembershipService._get_membership(membership_id, update=True)
        bind_context_dict(task=membership.task_id)

        requested_fields = set(validated_data.keys())
        logger.debug(f"Updating fields: {requested_fields}.")

        if not requested_fields:
            logger.warning("Validation error: Not allowed to update 0 fields.")
            raise ValidationError("Validation error: Task update failed.")

        if not TaskMembershipPolicy.can_update(actor, membership, requested_fields):
            logger.warning("Permission denied: Actor cannot update the task membership.")
            raise PermissionDenied(PERMISSION_DENIED_TO_UPDATE_TASK_MEMBERSHIP)

        for attr, value in validated_data.items():
            setattr(membership, attr, value)

        try:
            membership.full_clean()
            if fields := validated_data.keys():
                membership.save(update_fields=list(fields))
        except (ValidationError, IntegrityError) as exc:
            logger.warning(f"Validation error: can not update task membership. Reason: {exc}")
            raise

        logger.debug("Success: Task membership updated.")
        return membership
