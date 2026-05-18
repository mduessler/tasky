from typing import Any

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from loguru import logger
from registration.errors import EMAIL_VERIFICATION_TOKEN_DOES_NOT_EXIST
from registration.models import EmailVerificationToken
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import exception_handler
from task.errors import (
    TASK_DOES_NOT_EXIST,
    TASK_MEMBERSHIP_DOES_NOT_EXIST,
    TASK_NOTE_DOES_NOT_EXIST,
)
from task.models import Task, TaskMembership, TaskNote
from tms_auth.errors import USER_DOES_NOT_EXIST
from user.models import TmsUser


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:

    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        logger.debug(f"Throttled exception of {type(exc)}: {str(exc)}")
        data = {"detail": "Request was throttled."}
        if response:
            response.data = data
            response.status_code = 429
            return response
        return Response(
            data,
            status=HTTP_429_TOO_MANY_REQUESTS,
        )

    if isinstance(exc, DjangoPermissionDenied):
        logger.debug(f"Permission denied: {str(exc)}")
        return Response(
            {"detail": str(exc)},
            status=HTTP_403_FORBIDDEN,
        )

    if response is not None:
        logger.debug(f"DRF handled exception: {str(exc)}")
        return response

    if isinstance(exc, DjangoValidationError):
        logger.debug(f"Validation error: {exc.messages}")
        return Response(
            {"detail": exc.messages[0]},
            status=HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, TmsUser.DoesNotExist):
        logger.debug(USER_DOES_NOT_EXIST)
        return Response(
            {"detail": USER_DOES_NOT_EXIST},
            status=HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, Task.DoesNotExist):
        logger.debug(TASK_DOES_NOT_EXIST)
        return Response(
            {"detail": TASK_DOES_NOT_EXIST},
            status=HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, TaskMembership.DoesNotExist):
        logger.debug(TASK_MEMBERSHIP_DOES_NOT_EXIST)
        return Response(
            {"detail": TASK_MEMBERSHIP_DOES_NOT_EXIST},
            status=HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, TaskNote.DoesNotExist):
        logger.debug(TASK_NOTE_DOES_NOT_EXIST)
        return Response(
            {"detail": TASK_NOTE_DOES_NOT_EXIST},
            status=HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, EmailVerificationToken.DoesNotExist):
        logger.debug(EMAIL_VERIFICATION_TOKEN_DOES_NOT_EXIST)
        return Response(
            {"detail": EMAIL_VERIFICATION_TOKEN_DOES_NOT_EXIST},
            status=HTTP_404_NOT_FOUND,
        )

    logger.error(f"Unhandled exception of {type(exc)}: {str(exc)}")

    return Response(
        {"detail": "Internal server error"},
        status=HTTP_500_INTERNAL_SERVER_ERROR,
    )
