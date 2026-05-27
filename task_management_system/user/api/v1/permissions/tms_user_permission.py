from loguru import logger
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from user.models import TmsUser
from user.policies import TmsUserPolicy

from task_management_system.core.logging.utils import bind_context_dict


class TmsUserPermission(BasePermission):  # type: ignore[misc]
    def has_permission(self, request: Request, view: ModelViewSet) -> bool:
        if request.method in ("OPTIONS", "HEAD"):
            logger.debug("Has permission for action 'metadata': True.")
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
            case "retrieve" | "list" | "partial_update" | "destroy":
                result = True
            case _:
                logger.critical(f"Permission Denied: Unrecognized action '{view.action}'.")
                result = False

        logger.debug(f"Has permission for action '{view.action}': {result}")
        return result

    def has_object_permission(self, request: Request, view: ModelViewSet, user: TmsUser) -> bool:
        bind_context_dict(user=user.id)

        if not hasattr(view, "action"):
            logger.error("Permission Denied: View has no attribute 'action'.")
            return False

        bind_context_dict(action=view.action)
        actor = request.user
        match view.action:
            case "retrieve":
                result = TmsUserPolicy.can_view(actor, user)
            case "destroy":
                result = TmsUserPolicy.can_delete(actor, user)
            case "partial_update":
                result = True
            case _:
                logger.critical(f"Permission Denied: Unrecognized action '{view.action}'.")
                result = False

        logger.debug(f"Has user permission for action '{view.action}': {result}")
        return result  # type: ignore[no-any-return]
