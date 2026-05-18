from loguru import logger
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from task.models import TaskMembership
from task.policies import TaskMembershipPolicy

from task_management_system.core.logging.utils import bind_context_dict


class TaskMembershipPermission(BasePermission):  # type: ignore[misc]
    def has_permission(self, request: Request, view: ModelViewSet) -> bool:
        if request.method in ("OPTIONS", "HEAD"):
            return True

        if not request.user or not request.user.is_authenticated:
            logger.warning("User is not authenticated.")
            return False

        if not hasattr(view, "action"):
            logger.error("Permission Denied: View has no attribute 'action'.")
            return False

        bind_context_dict(action=view.action)

        match view.action:
            case "create" | "update":
                result = False
            case "list" | "retrieve" | "partial_update" | "destroy":
                result = TaskMembershipPolicy.can_access(request.user)
            case _:
                result = True
        logger.debug(f"Has permission for task membership action '{view.action}': {result}")
        return result

    def has_object_permission(
        self, request: Request, view: ModelViewSet, membership: TaskMembership
    ) -> bool:
        bind_context_dict(membership=membership.id, task=membership.task_id)

        if not hasattr(view, "action"):
            logger.error("Permission Denied: View has no attribute 'action'.")
            return False

        bind_context_dict(action=view.action)

        match view.action:
            case "retrieve":
                result = TaskMembershipPolicy.can_view(request.user, membership)
            case "destroy":
                result = TaskMembershipPolicy.can_delete(request.user, membership)
            case "partial_update":
                edit_able_fields = TaskMembershipPolicy.get_editable_fields(
                    request.user, membership
                )
                result = TaskMembershipPolicy.can_update(
                    request.user, membership, edit_able_fields
                )
            case _:
                logger.warning(f"Permission Denied: Unrecognized action '{view.action}'.")
                result = False

        logger.debug(f"Has object permission for task membership action '{view.action}': {result}")
        return result  # type: ignore[no-any-return]
