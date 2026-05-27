from django.db.models import Model
from loguru import logger
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View


class RegistrationBasePermission(BasePermission):  # type: ignore[misc]
    def has_permission(self, request: Request, _: View) -> bool:
        if request.method in ["OPTIONS", "HEAD"]:
            logger.debug("Permission granted: Request method in save methods.")
            return True

        if request.user.is_authenticated:
            logger.warning("Permission denied: Actor is already authenticated.")
            return False

        match request.method:
            case "POST":
                logger.debug("Permission granted: Has permission to register a new user.")
                return True
            case _:
                logger.warning("Permission denied: This method is not allowed in this view.")
                return False

    def has_object_permission(self, request: Request, view: View, obj: Model) -> bool:
        logger.warning(
            "Permission denied: This operation is not allowed in the registration views."
        )
        return False
