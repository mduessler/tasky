from datetime import timedelta

from django.utils import timezone
from loguru import logger
from task.models import Task, TaskMembership, TaskNote
from task.permissions import TaskNotePermissions
from task.selectors import get_actor_membership, get_role_for_user
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


class TaskNotePolicy:
    @staticmethod
    def can_access(actor: TmsUser) -> bool:
        if not isinstance(actor, TmsUser):
            logger.warning("Permission denied: User is not allowed to access task notes.")
            return False

        if actor.is_superuser:
            logger.info(
                "Permission granted: Actor is superuser and has permission to access notes."
            )
            return True

        if not TaskMembership.objects.filter(user=actor).exists():
            logger.debug("Permission denied: User is not allowed to access task notes.")
            return False

        logger.debug("Permission granted: User is allowed to access task notes.")
        return True

    @staticmethod
    def can_view(actor: TmsUser, note: TaskNote) -> bool:
        bind_context_dict(task=note.task_id, note=note.id)

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, note.task)):
            logger.warning("Permission denied: User has no membership for task.")
            return False
        bind_context_dict(actor_membership=actor_membership.id)

        result = TaskNotePermissions.get_view_permission(actor_membership.role)
        logger.debug(f"Permission granted to view task note: {result}.")
        return result  # type: ignore[no-any-return]

    @staticmethod
    def can_view_task_notes(actor: TmsUser) -> bool:
        if actor.is_superuser:
            logger.info("Permission granted to view all task notes: Actor is superuser.")
            return True

        logger.debug("Permission granted to view all task notes: False.")
        return False

    @staticmethod
    def can_create(actor: TmsUser, task: Task) -> bool:
        bind_context_dict(task=task.id)

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, task)):
            logger.warning("Permission denied: User has no membership for task.")
            return False

        bind_context_dict(actor_membership=actor_membership.id)

        result = TaskNotePermissions.get_create_permission(actor_membership.role)
        logger.debug(f"Permission granted to create task note: {result}.")
        return result  # type: ignore[no-any-return]

    @staticmethod
    def can_delete(actor: TmsUser, note: TaskNote) -> bool:
        bind_context_dict(task=note.task_id, note=note.id)

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, note.task)):
            logger.warning("Permission denied: User has no membership for task.")
            return False

        bind_context_dict(actor_membership=actor_membership.id)

        if (
            note.created_at > timezone.now() - timedelta(minutes=120)
            and actor.id == note.author_id
        ):
            logger.debug("Permission granted: Can delete own messages within 2 hours.")
            return True

        result = TaskNotePermissions.get_delete_permission(actor_membership.role)
        logger.debug(f"Permission granted to delete task note: {result}.")
        return result  # type: ignore[no-any-return]

    @staticmethod
    def can_update(actor: TmsUser, note: TaskNote, requested_fields: set[str]) -> bool:
        allowed_fields = {"note"}

        bind_context_dict(task=note.task_id, note=note.id)

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, note.task)):
            logger.warning("Permission denied: User has no membership for task.")
            return False

        bind_context_dict(actor_membership=actor_membership.id)

        if (
            note.created_at > timezone.now() - timedelta(minutes=120)
            and actor.id == note.author_id
        ):
            if not requested_fields.issubset(allowed_fields):
                logger.warning(
                    "Permission denied: Actor attempted to update membership restricted fields:"
                    f" {requested_fields - allowed_fields}"
                )
                return False
            logger.debug("Permission granted: Can update own messages within 2 hours.")
            return True

        if allowed_fields := TaskNotePermissions.get_update_permission(actor_membership.role):
            if not requested_fields.issubset(allowed_fields):
                logger.warning(
                    "Permission denied: Actor attempted to update membership restricted fields:"
                    f" {requested_fields - allowed_fields}."
                )
                return False
            logger.debug("Permission granted to update membership: True.")
            return True

        logger.debug("Permission granted to update task note: False.")
        return False

    @staticmethod
    def get_editable_fields(actor: TmsUser, note: TaskNote) -> set[str]:
        if not (role := get_role_for_user(actor, note.task)):
            return set()
        return TaskNotePermissions.get_update_permission(role)  # type: ignore[no-any-return]
