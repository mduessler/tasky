from loguru import logger
from task.models import Task, TaskMembership
from task.permissions import TaskMembershipPermissions
from task.selectors import get_actor_membership, get_role_for_user
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


class TaskMembershipPolicy:
    @staticmethod
    def can_access(actor: TmsUser) -> bool:
        if not isinstance(actor, TmsUser):
            logger.warning("Permission denied: User is not allowed to access task membersip.")
            return False

        if actor.is_superuser:
            logger.info(
                "Permission granted: Actor is superuser and has permission to access membership."
            )
            return True

        if not TaskMembership.objects.filter(user=actor).exists():
            logger.debug("Permission denied: User is not allowed to access task membersip.")
            return False

        logger.debug("Permission granted: User is allowed to access task memberships.")
        return True

    @staticmethod
    def has_permission_to_create(actor: TmsUser) -> bool:
        if not isinstance(actor, TmsUser):
            logger.warning(
                "Permission denied: User has not the permission to create a task membersip."
            )
            return False

        if actor.is_superuser:
            logger.info(
                "Permission granted: Actor is superuser and has permission to create membership."
            )
            return True

        allowed_roles = [
            role for role, value in TaskMembershipPermissions.create_permissions.items() if value
        ]
        result = TaskMembership.objects.filter(
            user=actor,
            role__in=allowed_roles,
        ).exists()

        logger.debug(f"Permission granted. Has permission to create a task membership: {result}.")
        return result  # type: ignore[no-any-return]

    @staticmethod
    def can_view(actor: TmsUser, membership: TaskMembership) -> bool:
        bind_context_dict(membership=membership.id, task=membership.task_id)

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser and can view membership.")
            return True

        if not (actor_membership := get_actor_membership(actor, membership.task)):
            logger.warning("Permission denied: Actor has no membership to view the membership.")
            return False
        bind_context_dict(actor_membership=actor_membership.id)

        if actor_membership.user_id == membership.user_id:
            logger.debug("Permission granted: User can view it's own membership.")
            return True

        result = TaskMembershipPermissions.get_view_permission(actor_membership.role)
        logger.debug(f"Permission to view membership: {result}.")
        return result  # type: ignore[no-any-return]

    @staticmethod
    def can_view_task_memberships(actor: TmsUser) -> bool:
        if actor.is_superuser:
            logger.info("Permission granted to view memberships: Actor is superuser.")
            return True

        logger.debug("Permission denied to view memberships: Actor is not superuser.")
        return False

    @staticmethod
    def can_create(actor: TmsUser, task: Task) -> bool:
        bind_context_dict(task=task.id)

        if actor.is_superuser:
            logger.info("Permission granted to create membership: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, task)):
            logger.warning(
                "Permission denied: Actor has no membership to create a task membership."
            )
            return False
        bind_context_dict(actor_membership=actor_membership.id)

        result = TaskMembershipPermissions.get_create_permission(actor_membership.role)
        logger.debug(f"Permission granted to create membership: {result}.")
        return result  # type: ignore[no-any-return]

    @staticmethod
    def can_delete(actor: TmsUser, membership: TaskMembership) -> bool:
        bind_context_dict(membership=membership.id, task=membership.task_id)

        if actor.is_superuser:
            logger.info("Permission granted to delete membership: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, membership.task)):
            logger.warning(
                "Permission denied: Actor has no membership to delete the task membership."
            )
            return False
        bind_context_dict(actor_membership=actor_membership.id)

        if actor.id == membership.user_id:
            logger.debug(
                "Permission granted to delete membership: User can delete it's own membership."
            )
            return True

        result = TaskMembershipPermissions.get_delete_permission(actor_membership.role)
        logger.debug(f"Permission granted to delete membership: {result}.")
        return result  # type: ignore[no-any-return]

    @staticmethod
    def can_update(actor: TmsUser, membership: TaskMembership, requested_fields: set[str]) -> bool:
        bind_context_dict(membership=membership.id, task=membership.task_id)

        if actor.is_superuser:
            logger.info("Permission granted to delete membership: Actor is superuser.")
            return True

        if not (actor_membership := get_actor_membership(actor, membership.task)):
            logger.warning(
                "Permission denied: Actor has no membership to update the task membership."
            )
            return False
        bind_context_dict(actor_membership=actor_membership.id)

        if allowed_fields := TaskMembershipPermissions.get_update_permission(
            actor_membership.role
        ):
            if not requested_fields.issubset(allowed_fields):
                logger.warning(
                    "Permission denied: Actor attempted to update membership restricted fields:"
                    f" {requested_fields - allowed_fields}."
                )
                return False
            logger.debug("Permission granted to update membership: True.")
            return True

        logger.debug(f"({actor_membership.role}, {requested_fields})")
        logger.debug("Permission granted to update membership: False.")
        return False

    @staticmethod
    def get_editable_fields(actor: TmsUser, membership: TaskMembership) -> set[str]:
        if not (role := get_role_for_user(actor, membership.task)):
            return set()
        return TaskMembershipPermissions.get_update_permission(role)  # type: ignore[no-any-return]
