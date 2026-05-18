from typing import Any

from django.core.exceptions import MultipleObjectsReturned, PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from loguru import logger
from registration.errors import (
    EMAIL_VERIFICATION_TOKEN_DOES_NOT_EXIST,
    PERMISSION_DENIED_TO_CREATE_AN_INACTIVE_USER,
    PERMISSION_DENIED_TO_VERIFY_VERIFICATION_TOKEN,
)
from registration.models import EmailVerificationToken
from registration.policies import RegistrationPolicy
from registration.tasks import send_verification_email_task
from rest_framework.exceptions import NotFound
from tms_auth.errors import USER_DOES_NOT_EXIST
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


class RegistrationService:

    @staticmethod
    def get_user_via_email(email: str) -> TmsUser:
        try:
            user = TmsUser.objects.select_for_update().get(email=email)
            bind_context_dict(user=user.id)
            logger.debug("Found: User exists.")
            return user
        except TmsUser.DoesNotExist as exc:
            logger.warning(f"Not found: User not found. Reaseon {exc}.")
            raise NotFound(USER_DOES_NOT_EXIST)
        except MultipleObjectsReturned as exc:
            logger.critical(f"Critical: Multiple Users returned! Reason {exc}.")
            raise

    @staticmethod
    def get_verification_token(user: TmsUser, token_raw: str) -> EmailVerificationToken:
        try:
            token = EmailVerificationToken.objects.select_for_update().get(
                user=user, token=token_raw
            )
            bind_context_dict(user=user.id, verification_token=token.id)
            logger.debug("Found: Token exists.")
            return token
        except EmailVerificationToken.DoesNotExist as exc:
            logger.warning(f"Not found: Token not found. Reason {exc}")
            raise NotFound(EMAIL_VERIFICATION_TOKEN_DOES_NOT_EXIST)
        except MultipleObjectsReturned as exc:
            logger.critical(f"Critical: Multiple Token returned! Reason {exc}.")
            raise

    @staticmethod
    @transaction.atomic  # type: ignore[misc]
    def register_user(validated_data: dict[str, Any]) -> TmsUser:
        if not RegistrationPolicy.can_register_user(validated_data):
            logger.warning("Permission denied: Not allowed to register user.")
            raise PermissionDenied(PERMISSION_DENIED_TO_CREATE_AN_INACTIVE_USER)
        try:
            user = TmsUser.objects.create_user(**validated_data)
            bind_context_dict(user=user.id)
            logger.debug("Success: Created an inactive user.")

            token = EmailVerificationToken(user=user)
            token.full_clean()
            token.save()
            bind_context_dict(verification_token=token.id)
            logger.debug("Success: Created a token for user.")

            transaction.on_commit(lambda: send_verification_email_task.delay(user.id, token.id))

            logger.debug("Success: Registered user.")
            return user
        except (ValidationError, IntegrityError) as exc:
            logger.warning(f"Validation error: Can not register user. Reason: {exc}")
            raise

    @classmethod
    @transaction.atomic  # type: ignore[misc]
    def activate_user(cls, email: str, token: str) -> TmsUser:
        user = cls.get_user_via_email(email)
        token_obj = cls.get_verification_token(user, token)

        if not RegistrationPolicy.can_verify_token(user, token_obj):
            logger.warning("Permission denied: Can not verify token.")
            raise PermissionDenied(PERMISSION_DENIED_TO_VERIFY_VERIFICATION_TOKEN)
        try:
            user.is_active = True
            user.full_clean()
            user.save()
            token_obj.delete()
        except (ValidationError, IntegrityError) as exc:
            logger.warning(f"Validation error: Can not activate user. Reason: {exc}")
            raise
        except ProtectedError as exc:
            logger.error(f"Protected error: Token deletion faild. Reason {exc}")
            raise ValidationError("Task cannot be deleted because it is still referenced")

        logger.debug("Success: User is activated now.")
        return user
