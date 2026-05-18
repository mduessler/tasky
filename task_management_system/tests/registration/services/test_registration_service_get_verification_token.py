import pytest
from django.core.exceptions import MultipleObjectsReturned
from django.db import connection
from django.test import utils
from registration.errors import EMAIL_VERIFICATION_TOKEN_DOES_NOT_EXIST
from registration.models import EmailVerificationToken
from registration.services import RegistrationService
from rest_framework.exceptions import NotFound
from tests.utils import assert_log


@pytest.mark.django_db
class TestGetVerificationToken:
    def test_success(self, inactive_user, email_token, caplog_loguru):
        result = RegistrationService.get_verification_token(inactive_user, email_token.token)

        assert isinstance(result, EmailVerificationToken)
        assert result.id == email_token.id

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Found: Token exists.",
            "DEBUG",
            user=inactive_user.id,
            verification_token=email_token.id,
        )

    def test_not_found(self, inactive_user, caplog_loguru):
        not_existing_token = "non-existing"

        with pytest.raises(NotFound) as exc:
            RegistrationService.get_verification_token(inactive_user, not_existing_token)

        assert EMAIL_VERIFICATION_TOKEN_DOES_NOT_EXIST == str(exc.value.detail)

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Not found: Token not found.", "WARNING")

    def test_multiple_objects_returned(
        self, inactive_user, email_token, monkeypatch, caplog_loguru
    ):
        def mock_get(*args, **kwargs):
            raise MultipleObjectsReturned("Multiple users found")

        monkeypatch.setattr(EmailVerificationToken.objects, "select_for_update", mock_get)

        with pytest.raises(MultipleObjectsReturned) as exc:
            RegistrationService.get_verification_token(inactive_user, email_token.token)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Critical: Multiple Token returned! Reason {exc.value}.",
            "CRITICAL",
        )

    def test_is_efficient(self, inactive_user, email_token):
        with utils.CaptureQueriesContext(connection) as queries:
            RegistrationService.get_verification_token(inactive_user, email_token.token)

        assert len(queries) <= 1
