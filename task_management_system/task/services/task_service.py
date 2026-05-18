from typing import Any

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.db.models.query import QuerySet
from loguru import logger
from rest_framework.exceptions import NotFound
from task.errors import (
    CAN_NOT_REOPEN_COMPLETE_TASK,
    PERMISSION_DENIED_TO_CREATE_TASK,
    PERMISSION_DENIED_TO_DELETE_TASK,
    PERMISSION_DENIED_TO_UPDATE_TASK,
    PERMISSION_DENIED_TO_VIEW_TASK,
    PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP,
    PERMISSION_DENIED_TO_VIEW_TASK_NOTE,
    TASK_DOES_NOT_EXIST,
)
from task.models import Role, Task, TaskMembership, TaskNote
from task.policies import TaskPolicy
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


class TaskService:
    @staticmethod
    def _get_task(task_id: int, update: bool = False) -> Task:
        try:
            if update:
                return Task.objects.select_for_update().get(pk=task_id)
            else:
                return Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            logger.warning("Not found: Task not found.")
            raise NotFound(TASK_DOES_NOT_EXIST)

    @staticmethod
    def get_task(actor: TmsUser, task_id: int) -> Task:
        bind_context_dict(task=task_id)

        task = TaskService._get_task(task_id)

        if not TaskPolicy.can_view(actor, task):
            logger.warning("Permission denied: Actor cannot view this task.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_TASK)

        logger.debug("Permission granted: Actor can view this task.")
        return task

    @staticmethod
    def get_tasks(actor: TmsUser, status: str | None = None) -> QuerySet[Task]:
        if not TaskPolicy.can_view_tasks(actor):
            logger.warning("Permission denied: Actor cannot view tasks.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_TASK)

        queryset = Task.objects.all()

        if status:
            queryset = queryset.filter(status=status)

        logger.debug(f"Tasks successfully retrieved with status {status}.")
        return queryset.distinct()

    @staticmethod
    def get_memberships_of_task(actor: TmsUser, task: Task) -> QuerySet[TaskMembership]:
        bind_context_dict(task=task.id)

        if not TaskPolicy.can_view_memberships_of_task(actor, task):
            logger.warning("Permission denied: Actor cannot view task memberships.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP)

        logger.debug("Permission granted: Actor can view task memberships.")
        return TaskMembership.objects.filter(task=task)

    @staticmethod
    def get_notes_of_task(actor: TmsUser, task: Task) -> QuerySet[TaskNote]:
        bind_context_dict(task=task.id)

        if not TaskPolicy.can_view_notes_of_task(actor, task):
            logger.warning("Permission denied: Actor cannot view this task notes.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_TASK_NOTE)

        logger.debug("Success: Getting notes of task.")
        return TaskNote.objects.filter(task=task)

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def create(actor: TmsUser, validated_data: dict[str, Any]) -> Task:

        logger.debug(f"Creating task with {validated_data}")

        if not TaskPolicy.can_create(actor):
            logger.warning("Permission denied: Actor cannot create a tasks")
            raise PermissionDenied(PERMISSION_DENIED_TO_CREATE_TASK)

        try:
            task = Task.objects.create(**validated_data)
            actor_membership = TaskMembership.objects.create(
                user=actor, task=task, role=Role.OWNER
            )

        except (ValidationError, IntegrityError) as exc:
            logger.warning(f"Validation error: can not create task. Reason: {exc}")
            raise

        bind_context_dict(task=task.id, actor_membership=actor_membership.id)
        logger.debug("Success: Task created.")
        return task

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def delete(actor: TmsUser, task_id: int) -> None:
        bind_context_dict(task=task_id)

        task = TaskService._get_task(task_id)

        if not TaskPolicy.can_delete(actor, task):
            logger.warning("Permission denied: Actor cannot delete the tasks")
            raise PermissionDenied(PERMISSION_DENIED_TO_DELETE_TASK)
        try:
            task.delete()
            logger.debug("Success: Task deleted.")
        except ProtectedError:
            logger.error("Protected error: Task deletion failed.")
            raise ValidationError("Task cannot be deleted because it is still referenced")

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def update(actor: TmsUser, task_id: int, validated_data: dict[str, Any]) -> Task:
        bind_context_dict(task=task_id)
        task = TaskService._get_task(task_id, update=True)

        requested_fields = set(validated_data.keys())
        logger.debug(f"Updating fields: {requested_fields}.")

        if not requested_fields:
            logger.warning("Validation error: Not allowed to update 0 fields.")
            raise ValidationError("Validation error: Task update failed.")

        if not TaskPolicy.can_update(actor, task, requested_fields):
            logger.warning("Permission denied: Actor cannot update the tasks")
            raise PermissionDenied(PERMISSION_DENIED_TO_UPDATE_TASK)

        if "status" in validated_data:
            if task.status == "done" and validated_data["status"] != "done":
                logger.warning("Validation error: Can not reopen an already closed task.")
                raise ValidationError(CAN_NOT_REOPEN_COMPLETE_TASK)

        for key, value in validated_data.items():
            setattr(task, key, value)
        try:
            task.full_clean()
            if fields := validated_data.keys():
                task.save(update_fields=list(fields))
        except (ValidationError, IntegrityError) as exc:
            logger.warning(f"Validation error: can not update task. Reason: {exc}")
            raise

        logger.debug("Success: Task updated.")
        return task
