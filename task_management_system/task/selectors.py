from loguru import logger
from task.models import Role, Task, TaskMembership
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


def get_role_for_user(actor: TmsUser, task: Task) -> Role | None:
    try:
        actor_membership = TaskMembership.objects.get(user=actor, task=task)
        return actor_membership.role
    except TaskMembership.DoesNotExist:
        logger.warning("Permission denied: Actor has no role for the task.")
        return None


def get_actor_membership(actor: TmsUser, task: Task) -> TaskMembership | None:
    bind_context_dict(task=task.id)

    if (
        hasattr(task, "_prefetched_objects_cache")
        and "memberships" in task._prefetched_objects_cache
    ):
        logger.debug("Using prefetched memberships for lookup.")

        for membership in task.memberships.all():
            if membership.user_id == actor.id:
                bind_context_dict(actor_membership=membership.id)
                logger.debug("Membership found via prefetch.")
                return membership

        logger.debug("No membership found in prefetched data.")
        return None

    try:
        membership = TaskMembership.objects.get(user=actor, task=task)
        bind_context_dict(actor_membership=membership.id)
        logger.debug("Membership found via DB query.")
        return membership
    except TaskMembership.DoesNotExist:
        logger.debug("No membership found via DB query.")
        return None
