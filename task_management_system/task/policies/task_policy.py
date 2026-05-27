from loguru import logger
from task.models import Task
from task.permissions import TaskMembershipPermissions, TaskNotePermissions, TaskPermissions
from task.selectors import get_actor_membership, get_role_for_user
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


class TaskPolicy:
    @staticmethod
    def can_access(actor: TmsUser) -> bool:
        if isinstance(actor, TmsUser):
            logger.debug("Permission granted: User is allowed to access tasks.")
            return True
        logger.debug("Permission denied: User is not allowed to access task.")
        return False

    @staticmethod
    def can_view(actor: TmsUser, task: Task) -> bool:
        bind_context_dict(task=task.id)

        if actor.is_superuser:
            logger.info("Permission granted to view task: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, task)):
            logger.warning("Permission denied to view task: User has no membership for task.")
            return False

        bind_context_dict(actor_membership=actor_membership.id)

        result = TaskPermissions.get_view_permission(actor_membership.role)
        logger.debug(f"Permission granted to view task: {result}.")
        return result  # type: ignore[no-any-return]

    @staticmethod
    def can_view_tasks(actor: TmsUser) -> bool:
        if actor.is_superuser:
            logger.info("Permission granted to view all tasks: Actor is superuser.")
            return True

        logger.debug("Permission granted to view task of user: False.")
        return False

    @staticmethod
    def can_view_memberships_of_task(actor: TmsUser, task: Task) -> bool:
        bind_context_dict(task=task.id)

        if actor.is_superuser:
            logger.info("Permission granted to view memberships of task: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, task)):
            logger.warning(
                "Permission denied: Actor has no membership to view the memberships of task."
            )
            return False
        bind_context_dict(actor_membership=actor_membership.id)

        result = TaskMembershipPermissions.get_view_permission(actor_membership.role)
        logger.debug(f"Permission granted to view memberships of task: {result}.")
        return result  # type: ignore[no-any-return]

    @staticmethod
    def can_view_notes_of_task(actor: TmsUser, task: Task) -> bool:
        bind_context_dict(task=task.id)

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, task)):
            logger.warning("Permission denied: User has no membership for task.")
            return False
        bind_context_dict(actor_membership=actor_membership.id)

        result = TaskNotePermissions.get_view_permission(actor_membership.role)
        logger.debug(f"Permission granted to view notes of task: {result}.")
        return result  # type: ignore[no-any-return]

    @staticmethod
    def can_create(actor: TmsUser) -> bool:
        if actor.is_superuser:
            logger.info("Permission granted to create task: Actor is superuser.")
            return True

        logger.debug("Permission granted to create task: True.")
        return True

    @staticmethod
    def can_delete(actor: TmsUser, task: Task) -> bool:
        bind_context_dict(task=task.id)

        if actor.is_superuser:
            logger.info("Permission granted to delete task: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, task)):
            logger.warning("Permission denied to delete task: User has no membership for task.")
            return False

        bind_context_dict(actor_membership=actor_membership.id)

        result = TaskPermissions.get_delete_permission(actor_membership.role)
        logger.debug(f"Permission granted to delete task: {result}.")

        return result  # type: ignore[no-any-return]

    @staticmethod
    def can_update(actor: TmsUser, task: Task, requested_fields: set[str]) -> bool:
        bind_context_dict(task=task.id)

        if actor.is_superuser:
            logger.info("Permission granted to update task: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, task)):
            logger.warning("Permission denied to update task: User has no membership for task.")
            return False

        bind_context_dict(actor_membership=actor_membership.id)

        if allowed_fields := TaskPermissions.get_update_permission(actor_membership.role):
            if not requested_fields.issubset(allowed_fields):
                logger.warning(
                    f"Permission denied: {actor_membership.role} actor attempted to update "
                    f"restricted fields: {requested_fields - allowed_fields}."
                )
                return False
            logger.debug("Permission granted to update task fields: True.")
            return True

        logger.debug("Permission granted to update task: False.")
        return False

    @staticmethod
    def get_editable_fields(actor: TmsUser, task: Task) -> set[str]:
        bind_context_dict(task=task.id)

        if not (role := get_role_for_user(actor, task)):
            return set()
        return TaskPermissions.get_update_permission(role)  # type: ignore[no-any-return]
