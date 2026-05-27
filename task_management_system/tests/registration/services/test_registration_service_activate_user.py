import pytest
from django.core.exceptions import MultipleObjectsReturned, PermissionDenied, ValidationError
from django.db import IntegrityError, connection
from django.db.models import ProtectedError
from django.test import utils
from registration.errors import PERMISSION_DENIED_TO_VERIFY_VERIFICATION_TOKEN
from registration.models import EmailVerificationToken
from registration.policies import RegistrationPolicy
from registration.services import RegistrationService
from rest_framework.exceptions import NotFound
from tests.utils import assert_log
from tms_auth.errors import USER_DOES_NOT_EXIST
from user.models import TmsUser


@pytest.mark.django_db
class TestVerifyVerificationToken:
    def test_success(self, email_token, caplog_loguru, monkeypatch):
        monkeypatch.setattr(RegistrationPolicy, "can_verify_token", lambda u_id, t: True)

        result = RegistrationService.activate_user(email_token.user.email, email_token.token)

        assert isinstance(result, TmsUser)
        assert result.id == email_token.user_id

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Success: User is activated now.",
            "DEBUG",
            user=email_token.user_id,
            verification_token=email_token.id,
        )

    def test_permission_denied(self, email_token, caplog_loguru, monkeypatch):
        monkeypatch.setattr(RegistrationPolicy, "can_verify_token", lambda u, t: False)

        with pytest.raises(PermissionDenied) as exc:
            RegistrationService.activate_user(email_token.user.email, email_token.token)
        assert PERMISSION_DENIED_TO_VERIFY_VERIFICATION_TOKEN == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Can not verify token.",
            "WARNING",
            user=email_token.user_id,
            verification_token=email_token.id,
        )

    def test_user_not_found(self, email_token, caplog_loguru):
        with pytest.raises(NotFound) as exc:
            RegistrationService.activate_user(9999, email_token.token)

        assert USER_DOES_NOT_EXIST == str(exc.value.detail)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Not found: User not found. Reason TmsUser matching query does not exist.",
            "WARNING",
        )

    def test_user_multiple_objects_returned(self, email_token, monkeypatch, caplog_loguru):
        def mock_get_user(*args, **kwargs):
            raise MultipleObjectsReturned("Multiple users found")

        monkeypatch.setattr(TmsUser.objects, "select_for_update", mock_get_user)

        with pytest.raises(MultipleObjectsReturned) as exc:
            RegistrationService.activate_user(email_token.user.email, email_token.token)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Critical: Multiple Users returned! Reason {exc.value}.",
            "CRITICAL",
        )

    def test_token_multiple_objects_returned(self, email_token, monkeypatch, caplog_loguru):
        from django.db.models.query import QuerySet

        def mock_get(*args, **kwargs):
            raise MultipleObjectsReturned("Multiple tokens found")

        monkeypatch.setattr(QuerySet, "get", mock_get)

        with pytest.raises(MultipleObjectsReturned):
            RegistrationService.activate_user(email_token.user.email, email_token.token)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Critical: Multiple Users returned! Reason Multiple tokens found.",
            "CRITICAL",
        )

    def test_validation_error(self, email_token, caplog_loguru, monkeypatch):
        def mock_full_clean(*args, **kwargs):
            raise ValidationError("Invalid token state")

        monkeypatch.setattr(TmsUser, "full_clean", mock_full_clean)

        with pytest.raises(ValidationError):
            RegistrationService.activate_user(email_token.user.email, email_token.token)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Validation error: Can not activate user.",
            "WARNING",
            verification_token=email_token.id,
            user=email_token.user_id,
        )

    def test_integrity_error(self, email_token, caplog_loguru, monkeypatch):
        def mock_save(*args, **kwargs):
            raise IntegrityError("Database constraint failed")

        monkeypatch.setattr(TmsUser, "full_clean", mock_save)

        with pytest.raises(IntegrityError):
            RegistrationService.activate_user(email_token.user.email, email_token.token)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Validation error: Can not activate user.",
            "WARNING",
            verification_token=email_token.id,
            user=email_token.user_id,
        )

    def test_protected_error(self, email_token, caplog_loguru, monkeypatch):
        def mock_delete(*args, **kwargs):
            raise ProtectedError("Database constraint failed", [email_token.user])

        monkeypatch.setattr(EmailVerificationToken, "delete", mock_delete)

        with pytest.raises(ProtectedError):
            RegistrationService.activate_user(email_token.user.email, email_token.token)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Validation error: Can not activate user.",
            "WARNING",
            verification_token=email_token.id,
            user=email_token.user_id,
        )

    def test_role_back(self, email_token, monkeypatch):
        def mock_delete(*args, **kwargs):
            raise ProtectedError("Database constraint failed", [email_token.user])

        monkeypatch.setattr(EmailVerificationToken, "delete", mock_delete)

        with pytest.raises(ProtectedError):
            RegistrationService.activate_user(email_token.user.email, email_token.token)

        email_token.user.refresh_from_db()
        assert email_token.user.is_active is False

    def test_is_efficient(self, email_token):
        with utils.CaptureQueriesContext(connection) as queries:
            RegistrationService.activate_user(email_token.user.email, email_token.token)

        assert len(queries) <= 8
