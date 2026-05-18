import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection
from django.test import utils
from registration.errors import PERMISSION_DENIED_TO_CREATE_AN_INACTIVE_USER
from registration.models import EmailVerificationToken
from registration.policies import RegistrationPolicy
from registration.services import RegistrationService
from tests.utils import assert_log
from user.models import TmsUser


@pytest.mark.django_db
class TestRegiserUser:
    def test_success(self, data, caplog_loguru):
        result = RegistrationService.register_user(data)

        assert isinstance(result, TmsUser)
        assert TmsUser.id is not None
        for key, value in data.items():
            if key == "password":
                continue
            assert getattr(result, key) == value

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Success: Registered user.", "DEBUG", user=result.id)

    def test_validation_error(self, data, caplog_loguru, monkeypatch):
        def mock_create(*args, **kwargs):
            raise ValidationError("Error")

        monkeypatch.setattr(TmsUser.objects, "create_user", mock_create)

        with pytest.raises(ValidationError) as exc:
            RegistrationService.register_user(data)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: Can not register user. Reason: {exc.value}",
            "WARNING",
        )

    def test_integrity_error(self, data, caplog_loguru, monkeypatch):
        def mock_create(*args, **kwargs):
            raise IntegrityError("Error")

        monkeypatch.setattr(TmsUser.objects, "create_user", mock_create)

        with pytest.raises(IntegrityError) as exc:
            RegistrationService.register_user(data)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: Can not register user. Reason: {exc.value}",
            "WARNING",
        )

    def test_permission_denied(self, data, caplog_loguru, monkeypatch):
        monkeypatch.setattr(RegistrationPolicy, "can_register_user", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            RegistrationService.register_user(data)
        assert PERMISSION_DENIED_TO_CREATE_AN_INACTIVE_USER == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Not allowed to register user.",
            "WARNING",
        )

    def test_validation_error_rollback(self, data, caplog_loguru, monkeypatch):
        def mock_full_clean(*args, **kwargs):
            raise ValidationError("Invalid token state")

        cnt = TmsUser.objects.all().count()
        monkeypatch.setattr(EmailVerificationToken, "full_clean", mock_full_clean)

        with pytest.raises(ValidationError) as exc:
            RegistrationService.register_user(data)

        assert cnt == TmsUser.objects.all().count()

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: Can not register user. Reason: {exc.value}",
            "WARNING",
        )

    def test_integrity_error_rollback(self, data, caplog_loguru, monkeypatch):
        def mock_save(*args, **kwargs):
            raise IntegrityError("Database constraint failed")

        cnt = TmsUser.objects.all().count()
        monkeypatch.setattr(EmailVerificationToken, "save", mock_save)

        with pytest.raises(IntegrityError) as exc:
            RegistrationService.register_user(data)

        assert cnt == TmsUser.objects.all().count()
        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: Can not register user. Reason: {exc.value}",
            "WARNING",
        )

    def test_is_efficient(self, data):
        with utils.CaptureQueriesContext(connection) as queries:
            RegistrationPolicy.can_register_user(data)

        assert len(queries) <= 1
