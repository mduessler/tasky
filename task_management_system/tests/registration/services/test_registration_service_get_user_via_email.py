import pytest
from django.core.exceptions import MultipleObjectsReturned
from django.db import connection
from django.test import utils
from registration.services import RegistrationService
from rest_framework.exceptions import NotFound
from tests.utils import assert_log
from tms_auth.errors import USER_DOES_NOT_EXIST
from user.models import TmsUser


@pytest.mark.django_db
class TestGetUserViaEmail:
    def test_success(self, inactive_user, email_token, caplog_loguru):
        result = RegistrationService.get_user_via_email(inactive_user.email)

        assert isinstance(result, TmsUser)
        assert result.id == email_token.user.id

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Found: User exists.",
            "DEBUG",
            user=email_token.user_id,
        )

    def test_not_found(self, caplog_loguru):
        with pytest.raises(NotFound) as exc:
            RegistrationService.get_user_via_email("fake@fake-email.he")

        assert USER_DOES_NOT_EXIST == str(exc.value.detail)

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Not found: User not found.", "WARNING")

    def test_multiple_objects_returned(self, inactive_user, monkeypatch, caplog_loguru):
        def mock_get(*args, **kwargs):
            raise MultipleObjectsReturned("Multiple users found")

        monkeypatch.setattr(TmsUser.objects, "select_for_update", mock_get)

        with pytest.raises(MultipleObjectsReturned) as exc:
            RegistrationService.get_user_via_email(inactive_user.email)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Critical: Multiple Users returned! Reason {exc.value}.",
            "CRITICAL",
        )

    def test_is_efficient(self, inactive_user):
        with utils.CaptureQueriesContext(connection) as queries:
            RegistrationService.get_user_via_email(inactive_user.email)

        assert len(queries) <= 1
