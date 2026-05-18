import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection
from django.db.models.deletion import ProtectedError
from django.test import utils
from tests.utils import assert_log
from user.errors import PERMISSION_DENIED_TO_DELETE_USER
from user.models import TmsUser
from user.policies import TmsUserPolicy
from user.services import TmsUserService


@pytest.mark.django_db
class TestDelete:
    def test_success(self, member_is_owner, superuser, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner
        user_id = superuser.id

        monkeypatch.setattr(TmsUserPolicy, "can_delete", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)

        TmsUserService.delete(actor, superuser.id)

        assert TmsUser.objects.filter(id=user_id).exists() is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Success: User deleted.",
            "DEBUG",
            user=user_id,
        )

    def test_permission_denied(self, user_is_not_member, superuser, caplog_loguru, monkeypatch):
        actor, _ = user_is_not_member
        user_id = superuser.id

        monkeypatch.setattr(TmsUserPolicy, "can_delete", lambda *a, **k: False)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)

        with pytest.raises(PermissionDenied) as exc:
            TmsUserService.delete(actor, superuser.id)

        assert PERMISSION_DENIED_TO_DELETE_USER == str(exc.value)
        assert TmsUser.objects.filter(id=user_id).exists() is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Not allowed to delete user.",
            "WARNING",
            user=user_id,
        )

    def test_protected_error(self, member_is_owner, superuser, caplog_loguru, monkeypatch):
        def mock_delete(self):
            raise ProtectedError("Error", TmsUser.objects.none())

        actor, _ = member_is_owner
        user_id = superuser.id

        monkeypatch.setattr(TmsUserPolicy, "can_delete", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)
        monkeypatch.setattr(TmsUser, "delete", mock_delete)

        with pytest.raises(ValidationError):
            TmsUserService.delete(actor, superuser.id)
        assert TmsUser.objects.filter(id=user_id).exists() is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Protected error: User deletion failed.",
            "ERROR",
            user=user_id,
        )

    def test_atomicity_on_error(self, member_is_owner, superuser, monkeypatch):
        def mock_delete(self):
            raise ProtectedError("Error", {"protected"})

        actor, _ = member_is_owner
        user_id = superuser.id

        monkeypatch.setattr(TmsUserPolicy, "can_delete", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)
        monkeypatch.setattr(TmsUser, "delete", mock_delete)

        with pytest.raises(ValidationError):
            TmsUserService.delete(actor, superuser.id)
        assert TmsUser.objects.filter(pk=user_id).exists() is True

    def test_is_efficient(self, member_is_owner, superuser, monkeypatch):
        user, _ = member_is_owner

        monkeypatch.setattr(TmsUserPolicy, "can_delete", lambda *a, **k: True)
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TmsUserService.delete(superuser, user.id)

        assert len(queries) <= 11
