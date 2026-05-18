from unittest.mock import patch

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection
from django.test import utils
from rest_framework.exceptions import NotFound
from tests.utils import assert_log
from user.models import TmsUser
from user.policies import TmsUserPolicy
from user.services import TmsUserService


@pytest.mark.django_db
class TestUpdateTmsUser:
    def test_update_success(self, active_user, inactive_user, caplog_loguru, monkeypatch):
        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": "max-fake@example.com",
        }

        monkeypatch.setattr(TmsUserPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)

        TmsUserService.update(active_user, inactive_user.id, data)

        inactive_user.refresh_from_db()
        assert inactive_user.first_name == "Max"
        assert inactive_user.email == "max-fake@example.com"

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Success: User updated.", "DEBUG", user=inactive_user.id)

    def test_password_hashing(self, active_user, inactive_user, caplog_loguru, monkeypatch):
        raw_pw = "secret123"

        monkeypatch.setattr(TmsUserPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)

        TmsUserService.update(active_user, inactive_user.id, {"password": raw_pw})

        inactive_user.refresh_from_db()
        assert inactive_user.password != raw_pw
        assert inactive_user.check_password(raw_pw)

        log_record = caplog_loguru.records[-2]
        assert_log(log_record, "Updating password.", "DEBUG", user=inactive_user.id)

    def test_permission_denied(self, active_user, inactive_user, caplog_loguru, monkeypatch):
        monkeypatch.setattr(TmsUserPolicy, "can_update", lambda *a, **k: False)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)

        with pytest.raises(PermissionDenied):
            TmsUserService.update(active_user, inactive_user.id, {"first_name": "Roooobert"})

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Not allowed to update fields.",
            "WARNING",
            user=inactive_user.id,
        )

    @patch("user.policies.TmsUserPolicy.can_update")
    def test_policy_receives_correct_fields(
        self, mock_can_update, superuser, inactive_user, monkeypatch
    ):
        mock_can_update.return_value = True
        data = {"first_name": "max", "username": "very-important@example.com"}

        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)

        TmsUserService.update(superuser, inactive_user.id, data)

        mock_can_update.assert_called_once_with(superuser, inactive_user, set(data.keys()))

    def test_user_not_found(self, active_user, caplog_loguru):
        with pytest.raises(NotFound):
            TmsUserService.update(active_user, 99999, {"first_name": "None"})

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Not found: User does not exist.",
            "WARNING",
            user=99999,
        )

    def test_validation_error_handling(
        self, active_user, inactive_user, caplog_loguru, monkeypatch
    ):
        def mock_save(self, *args, **kwargs):
            raise ValidationError("Invalid Data")

        monkeypatch.setattr(TmsUserPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)
        monkeypatch.setattr(TmsUser, "save", mock_save)

        with pytest.raises(ValidationError):
            TmsUserService.update(active_user, inactive_user.id, {"first_name": "X"})

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Validation error: can not update user. Reason:",
            "WARNING",
            user=inactive_user.id,
        )

    def test_integrity_error_handling(
        self, active_user, inactive_user, caplog_loguru, monkeypatch
    ):
        def mock_full_clean(*args, **kwargs):
            raise IntegrityError("Duplicate Email")

        monkeypatch.setattr(TmsUserPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)
        monkeypatch.setattr(TmsUser, "full_clean", mock_full_clean)

        with pytest.raises(IntegrityError):
            TmsUserService.update(active_user, inactive_user.id, {"email": "dup@test.com"})

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Validation error: can not update user. Reason:",
            "WARNING",
            user=inactive_user.id,
        )

    def test_transaction_rollback(self, active_user, inactive_user, monkeypatch):
        def mock_full_clean(*args, **kwargs):
            raise IntegrityError("Duplicate Email")

        original_name = inactive_user.first_name

        monkeypatch.setattr(TmsUserPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)
        monkeypatch.setattr(TmsUser, "full_clean", mock_full_clean)

        with pytest.raises(Exception):
            TmsUserService.update(active_user, inactive_user.id, {"first_name": "Changed"})

        inactive_user.refresh_from_db()
        assert inactive_user.first_name == original_name

    @patch.object(TmsUser, "save")
    def test_update_fields_usage(self, mock_save, active_user, inactive_user, monkeypatch):
        monkeypatch.setattr(TmsUserPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)

        TmsUserService.update(active_user, inactive_user.id, {"first_name": "New"})
        _, kwargs = mock_save.call_args
        assert "first_name" in kwargs["update_fields"]

    def test_query_count_efficiency(self, active_user, inactive_user, monkeypatch):
        monkeypatch.setattr(TmsUserPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TmsUserService.update(active_user, inactive_user.id, {"first_name": "Fast"})

        assert len(queries) <= 5

    def test_empty_data_no_save(self, active_user, inactive_user, monkeypatch):
        monkeypatch.setattr(TmsUserPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TmsUserService.update(active_user, inactive_user.id, {})

        update_queries = [q for q in queries if "UPDATE" in q["sql"]]
        assert len(update_queries) == 0

    def test_password_only_update(self, active_user, inactive_user, monkeypatch):
        monkeypatch.setattr(TmsUserPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)

        TmsUserService.update(active_user, inactive_user.id, {"password": "new_password_only"})

        inactive_user.refresh_from_db()
        assert inactive_user.check_password("new_password_only")
