import pytest
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from registration.errors import EMAIL_VERIFICATION_TOKEN_DOES_NOT_EXIST
from registration.models import EmailVerificationToken
from rest_framework.exceptions import NotFound
from task.errors import (
    TASK_DOES_NOT_EXIST,
    TASK_MEMBERSHIP_DOES_NOT_EXIST,
    TASK_NOTE_DOES_NOT_EXIST,
)
from task.models import Task, TaskMembership, TaskNote
from tests.utils import DummyView, assert_log, build_request
from tms_auth.errors import USER_DOES_NOT_EXIST
from user.models import TmsUser

from task_management_system.core.exceptions import custom_exception_handler


@pytest.fixture(autouse=True)
def context(active_user):
    request = build_request(
        method="get", user=active_user, path="/just/", query_params={"user": 5, "task": 2}
    )
    return {
        "request": request,
        "view": DummyView(),
    }


@pytest.mark.django_db
class TestCustomExceptionHandler:
    def test_drf_exception_passthrough(self, caplog_loguru):
        exc = NotFound("not found")

        response = custom_exception_handler(exc, context)

        assert response.status_code == 404
        assert response.data["detail"] == "not found"

        record = caplog_loguru.records[-1]
        assert_log(record, f"DRF handled exception: {str(exc)}", "DEBUG")

    def test_validation_error(self, caplog_loguru):
        exc = DjangoValidationError("invalid input")

        response = custom_exception_handler(exc, context)

        assert response.status_code == 400
        assert response.data == {"detail": "invalid input"}

        record = caplog_loguru.records[-1]
        assert_log(record, f"Validation error: {exc.messages}", "DEBUG")

    def test_permission_denied(self, caplog_loguru):
        exc = DjangoPermissionDenied("forbidden")

        response = custom_exception_handler(exc, context)

        assert response.status_code == 403
        assert response.data == {"detail": "forbidden"}

        record = caplog_loguru.records[-1]
        assert_log(record, f"Permission denied: {str(exc)}", "DEBUG")

    @pytest.mark.parametrize(
        "exception, expected_detail",
        [
            (TmsUser.DoesNotExist(), USER_DOES_NOT_EXIST),
            (Task.DoesNotExist(), TASK_DOES_NOT_EXIST),
            (TaskMembership.DoesNotExist(), TASK_MEMBERSHIP_DOES_NOT_EXIST),
            (TaskNote.DoesNotExist(), TASK_NOTE_DOES_NOT_EXIST),
            (EmailVerificationToken.DoesNotExist(), EMAIL_VERIFICATION_TOKEN_DOES_NOT_EXIST),
        ],
    )
    def test_not_found_exceptions(self, exception, expected_detail, caplog_loguru):
        response = custom_exception_handler(exception, context)

        assert response.status_code == 404
        assert response.data["detail"] == expected_detail

        record = caplog_loguru.records[-1]
        assert_log(record, str(expected_detail), "DEBUG")

    def test_unhandled_exception_returns_500(self, caplog_loguru):
        exc = Exception("boom")

        response = custom_exception_handler(exc, context)

        assert response.status_code == 500
        assert response.data == {"detail": "Internal server error"}

        record = caplog_loguru.records[-1]
        assert_log(record, "Unhandled exception of <class 'Exception'>: boom", "ERROR")
