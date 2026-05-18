from typing import Any

from loguru import logger
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


class TmsUserPolicy:
    @staticmethod
    def bind_log_context(**kwargs: Any) -> Any:
        return bind_context_dict("tms_user_policy", **kwargs)

    @staticmethod
    def can_view(actor: TmsUser, user: TmsUser) -> bool:
        bind_context_dict(user=user.id)

        if actor.id == user.id:
            logger.debug("Permission granted: Actor is user and can view user.")
            return True

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser and can view user.")
            return True

        logger.warning("Permission denied: Actor is not allowed to view the user.")
        return False

    @staticmethod
    def can_create(actor: TmsUser) -> bool:

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser and can create a user.")
            return True

        logger.warning("Permission denied: Actor is not allowed to create a user.")
        return False

    @staticmethod
    def can_delete(actor: TmsUser, user: TmsUser) -> bool:
        bind_context_dict(user=user.id)

        if actor.id == user.id:
            logger.debug("Permission granted: Actor is user and can delete.")
            return True

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser and can delete.")
            return True

        logger.warning("Permission denied: Actor is not allowed to delete the user.")
        return False

    @staticmethod
    def can_update(actor: TmsUser, user: TmsUser, requested_fields: set[str]) -> bool:
        bind_context_dict(user=user.id)

        if actor.id == user.id:
            allowed_fields = {"email", "username", "password", "lastname", "firstname"}

            if not requested_fields.issubset(allowed_fields):
                logger.warning(
                    "Permission denied: Actor attempted to update restricted fields: "
                    f"{requested_fields - allowed_fields}"
                )
                return False

            logger.debug("Permission granted: Actor is updating allowed fields on themselves.")
            return True

        if actor.is_superuser:
            logger.info("Permission granted: Actor is superuser and can update.")
            return True

        logger.warning("Permission denied: Actor is not allowed to update the user.")
        return False
