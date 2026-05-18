from loguru import logger
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from task.models import TaskNote
from task.policies import TaskNotePolicy

from task_management_system.core.logging.utils import bind_context_dict


class TaskNotePermission(BasePermission):  # type: ignore[misc]
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
                result = TaskNotePolicy.can_access(request.user)
            case _:
                result = True
        logger.debug(f"Has permission for task note action '{view.action}': {result}")
        return result

    def has_object_permission(self, request: Request, view: ModelViewSet, note: TaskNote) -> bool:
        bind_context_dict(note=note.id, task=note.task_id)

        if not hasattr(view, "action"):
            logger.error("Permission Denied: View has no attribute 'action'.")
            return False

        bind_context_dict(action=view.action)

        match view.action:
            case "retrieve":
                result = TaskNotePolicy.can_view(request.user, note)
            case "destroy":
                result = TaskNotePolicy.can_delete(request.user, note)
            case "partial_update":
                edit_able_fields = TaskNotePolicy.get_editable_fields(request.user, note)
                result = TaskNotePolicy.can_update(request.user, note, edit_able_fields)
            case _:
                logger.warning(f"Permission Denied: Unrecognized action '{view.action}'.")
                result = False

        logger.debug(f"Has object permission for task note action '{view.action}': {result}")
        return result  # type: ignore[no-any-return]
