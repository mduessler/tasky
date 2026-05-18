from typing import Any

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, QuerySet
from loguru import logger
from rest_framework.exceptions import NotFound
from task.errors import (
    PERMISSION_DENIED_TO_CREATE_TASK_NOTE,
    PERMISSION_DENIED_TO_DELETE_TASK_NOTE,
    PERMISSION_DENIED_TO_UPDATE_TASK_NOTE,
    PERMISSION_DENIED_TO_VIEW_TASK_NOTE,
    TASK_NOTE_DOES_NOT_EXIST,
)
from task.models import Task, TaskNote
from task.policies import TaskNotePolicy
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


class TaskNoteService:
    @staticmethod
    def _get_note(note_id: int, update: bool = False) -> Task:
        try:
            if update:
                return TaskNote.objects.select_for_update().get(pk=note_id)
            else:
                return TaskNote.objects.get(pk=note_id)
        except TaskNote.DoesNotExist:
            logger.warning("Not found: Task note not found.")
            raise NotFound(TASK_NOTE_DOES_NOT_EXIST)

    @staticmethod
    def get_task_note(actor: TmsUser, note_id: int) -> TaskNote:
        bind_context_dict(note=note_id)

        note = TaskNoteService._get_note(note_id)
        bind_context_dict(task=note.task_id)

        if not TaskNotePolicy.can_view(actor, note):
            logger.warning("Permission denied: Actor cannot view this task note.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_TASK_NOTE)

        logger.debug("Permission granted: Actor can view this task note.")
        return note

    @staticmethod
    def get_task_notes(actor: TmsUser) -> QuerySet[TaskNote]:
        if not TaskNotePolicy.can_view_task_notes(actor):
            logger.warning("Permission denied: Actor cannot view all task notes.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VIEW_TASK_NOTE)

        logger.debug("Success: Getting all task notes.")
        return TaskNote.objects.all()

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def create(actor: TmsUser, validated_data: dict[str, Any]) -> TaskNote:
        bind_context_dict(task=validated_data["task"].id)

        if not TaskNotePolicy.can_create(actor, validated_data["task"]):
            logger.warning("Permission denied: Actor cannot create task note.")
            raise PermissionDenied(PERMISSION_DENIED_TO_CREATE_TASK_NOTE)

        try:
            note = TaskNote.objects.create(**validated_data)
            bind_context_dict(note=note.id)
        except (ValidationError, IntegrityError) as exc:
            logger.warning(f"Validation error: can not create task note. Reason: {exc}")
            raise

        logger.debug("Success: Task note created.")
        return note

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def delete(actor: TmsUser, note_id: int) -> None:
        bind_context_dict(note=note_id)

        note = TaskNoteService._get_note(note_id)
        bind_context_dict(task=note.task_id)

        if not TaskNotePolicy.can_delete(actor, note):
            logger.warning("Permission denied: Actor cannot delete task note.")
            raise PermissionDenied(PERMISSION_DENIED_TO_DELETE_TASK_NOTE)

        try:
            note.delete()
            logger.debug("Success: Task note deleted.")
        except ProtectedError:
            logger.error("Protected error: Task note deletion failed.")
            raise ValidationError("Task note cannot be deleted because it is still referenced")

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def update(actor: TmsUser, note_id: int, validated_data: dict[str, Any]) -> TaskNote:
        bind_context_dict(note=note_id)

        note = TaskNoteService._get_note(note_id, update=True)
        bind_context_dict(task=note.task_id)

        requested_fields = set(validated_data.keys())
        logger.debug(f"Updating fields: {requested_fields}.")

        if not requested_fields:
            logger.warning("Validation error: Not allowed to update 0 fields.")
            raise ValidationError("Validation error: Task note update failed.")

        if not TaskNotePolicy.can_update(actor, note, requested_fields):
            logger.warning("Permission denied: Actor cannot delete task note.")
            raise PermissionDenied(PERMISSION_DENIED_TO_UPDATE_TASK_NOTE)

        for key, value in validated_data.items():
            setattr(note, key, value)

        try:
            note.full_clean()
            if fields := validated_data.keys():
                note.save(update_fields=list(fields))
        except (ValidationError, IntegrityError) as exc:
            logger.warning(f"Validation error: can not update task note. Reason: {exc}")
            raise

        logger.debug("Success: Task note updated.")
        return note
