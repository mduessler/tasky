from typing import Any

from loguru import logger
from registration.models import EmailVerificationToken
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


class RegistrationPolicy:
    @staticmethod
    def can_register_user(validated_data: dict[str, Any]) -> bool:
        if TmsUser.objects.filter(email=validated_data["email"]).exists():
            logger.warning("Permission denied: A user with the given email already exists.")
            return False

        logger.debug("Allowed: Can create an inactive user.")
        return True

    @staticmethod
    def can_verify_token(user: TmsUser, token: EmailVerificationToken) -> bool:
        bind_context_dict(user=user.id, verification_token=token.id)

        if user.is_active:
            logger.warning(
                "Permission denied: Can not verify verification token. User is already activated."
            )
            return False
        if token.is_expired():
            logger.warning("Permission denied: Verification token is expired.")
            return False
        if token.user != user:
            logger.warning("Permission denied: Verification token does not belong to user.")
            return False

        logger.debug("Allowed: Can verify token.")
        return True
