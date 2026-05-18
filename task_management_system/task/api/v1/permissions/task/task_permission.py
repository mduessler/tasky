from loguru import logger
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from task.models import Task
from task.policies import TaskMembershipPolicy, TaskNotePolicy, TaskPolicy

from task_management_system.core.logging.utils import bind_context_dict


class TaskPermission(BasePermission):  # type: ignore[misc]
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
        user = request.user

        match view.action:
            case "create":
                result = TaskPolicy.can_create(user)
            case "retrieve" | "list" | "partial_update" | "destroy":
                result = TaskPolicy.can_access(user)
            case "membership" | "memberships":
                result = TaskMembershipPolicy.can_access(user)
            case "note" | "notes":
                result = TaskNotePolicy.can_access(user)
            case "update":
                result = False
            case _:
                result = True
        logger.debug(f"Has permission for action '{view.action}': {result}")
        return result  # type: ignore[no-any-return]

    def has_object_permission(self, request: Request, view: ModelViewSet, task: Task) -> bool:
        bind_context_dict(task=task.id)

        if not hasattr(view, "action"):
            logger.error("Permission Denied: View has no attribute 'action'.")
            return False

        bind_context_dict(action=view.action)
        user = request.user

        match view.action:
            case "create" | "list":
                result = False
            case "retrieve":
                result = TaskPolicy.can_view(user, task)
            case "destroy":
                result = TaskPolicy.can_delete(user, task)
            case "partial_update":
                edit_able_fields = TaskPolicy.get_editable_fields(user, task)
                result = TaskPolicy.can_update(user, task, edit_able_fields)
            case "membership":
                result = TaskMembershipPolicy.can_create(user, task)
            case "note":
                result = TaskNotePolicy.can_create(user, task)
            case _:
                logger.warning(f"Permission Denied: Unrecognized action '{view.action}'.")
                result = False

        logger.debug(f"Has object permission for action '{view.action}': {result}")
        return result
