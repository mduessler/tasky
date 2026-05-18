from loguru import logger
from task.models import Task
from user.models import TmsUser
from user.permissions import TmsUserPermission

from task_management_system.core.logging.utils import bind_context_dict


class TmsUserPolicy:
    @staticmethod
    def can_view(actor: TmsUser, user: TmsUser) -> bool:
        bind_context_dict(user=user.id)

        if actor.id == user.id:
            logger.debug("Permission granted: User can view itself.")
            return TmsUserPermission.get_view_permission("self")  # type: ignore[no-any-return]

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser and can view user.")
            return TmsUserPermission.get_view_permission("superuser")  # type: ignore

        if Task.objects.filter(memberships__user=actor).filter(memberships__user=user).exists():
            logger.debug("Permission granted: Actor and user work on the same task.")
            return TmsUserPermission.get_view_permission("group-member")  # type: ignore

        logger.debug("Permission denied: Actor is not allowed to view user.")
        return TmsUserPermission.get_view_permission("other")  # type: ignore[no-any-return]

    @staticmethod
    def can_view_users(actor: TmsUser) -> bool:
        bind_context_dict(user=actor.id)
        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser and can view user.")
            return TmsUserPermission.get_view_permission("superuser")  # type: ignore

        logger.debug("Permission denied: Actor is not allowed to view user.")
        return TmsUserPermission.get_view_permission("other")  # type: ignore[no-any-return]

    @staticmethod
    def can_view_tasks_of_user(actor: TmsUser, user: TmsUser) -> bool:
        bind_context_dict(user=user.id)

        if actor.id == user.id:
            logger.debug("Permission granted: User can view it's own tasks.")
            return True

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser and can view user tasks.")
            return True

        logger.debug("Permission denied: Actor is not allowed to view user tasks.")
        return False

    @staticmethod
    def can_view_memberships_of_user(actor: TmsUser, user: TmsUser) -> bool:
        bind_context_dict(user=user.id)

        if actor.id == user.id:
            logger.debug("Permission granted: User can view it's own task memberships.")
            return True

        if actor.is_superuser:
            logger.info(
                "Permission granted: Actor is superuser and can view user task memberships."
            )
            return True

        logger.debug("Permission denied: Actor is not allowed to view user memberships.")
        return TmsUserPermission.get_view_permission("other")  # type: ignore[no-any-return]

    @staticmethod
    def can_view_notes_of_user(actor: TmsUser, user: TmsUser) -> bool:
        bind_context_dict(user=user.id)

        if actor.id == user.id:
            logger.debug("Permission granted: User can view it's own task notes.")
            return True

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser and can view user task notes.")
            return True

        logger.debug("Permission denied: Actor is not allowed to view user notes.")
        return TmsUserPermission.get_view_permission("other")  # type: ignore[no-any-return]

    @staticmethod
    def can_delete(actor: TmsUser, user: TmsUser) -> bool:
        bind_context_dict(user=user.id)

        if actor.id == user.id:
            logger.debug("Permission granted: User can delete itself.")
            return TmsUserPermission.get_delete_permission("self")  # type: ignore[no-any-return]

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser and can delete user.")
            return TmsUserPermission.get_delete_permission("superuser")  # type: ignore

        logger.debug("Permission denied: Actor is not allowed to delete user.")
        return TmsUserPermission.get_delete_permission("other")  # type: ignore[no-any-return]

    @staticmethod
    def can_update(actor: TmsUser, user: TmsUser, requested_fields: set[str]) -> bool:
        bind_context_dict(user=user.id)

        if actor.id == user.id:
            allowed_fields = TmsUserPermission.get_update_permission("self")
            result = requested_fields.issubset(allowed_fields)
            logger.debug(f"Permission granted: User can update itself {result}.")
            return result

        if actor.is_superuser:
            allowed_fields = TmsUserPermission.get_update_permission("superuser")
            result = requested_fields.issubset(allowed_fields)
            logger.info(f"Permission granted: Actor is superuser and can update user {result}.")
            return result

        allowed_fields = TmsUserPermission.get_update_permission("other")
        result = True if requested_fields and requested_fields.issubset(allowed_fields) else False

        logger.debug(f"Permission denied: Actor is not allowed to delete user {result}.")
        return result

    @staticmethod
    def get_editable_fields(actor: TmsUser, user: TmsUser) -> set[str]:
        bind_context_dict(user=user.id)

        if actor.id == user.id:
            logger.debug("Getting update permission for 'self'.")
            return TmsUserPermission.get_update_permission("self")  # type: ignore[no-any-return]
        elif actor.is_superuser:
            logger.debug("Getting update permission for 'superuser'.")
            return TmsUserPermission.get_update_permission("superuser")  # type: ignore
        elif Task.objects.filter(memberships__user=actor).filter(memberships__user=user).exists():
            logger.debug("Getting update permission for 'group-member'.")
            return TmsUserPermission.get_update_permission("group-member")  # type: ignore
        else:
            logger.debug("Getting update permission for 'other'.")
            return TmsUserPermission.get_update_permission("other")  # type: ignore[no-any-return]
