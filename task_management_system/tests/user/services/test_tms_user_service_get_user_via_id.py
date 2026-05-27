import pytest
from django.core.exceptions import MultipleObjectsReturned, PermissionDenied
from django.db import connection
from django.test import utils
from rest_framework.exceptions import NotFound
from tests.utils import assert_log
from tms_auth.errors import USER_DOES_NOT_EXIST
from user.errors import PERMISSION_DENIED_TO_VIEW_USER
from user.models import TmsUser
from user.policies import TmsUserPolicy
from user.services import TmsUserService


@pytest.mark.django_db
class TestGetUserViaId:
    def test_success(self, superuser_read_only, active_user_read_only, caplog_loguru):
        result = TmsUserService.get_user_via_id(superuser_read_only, active_user_read_only.id)

        assert isinstance(result, TmsUser)
        assert result.id == active_user_read_only.id

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Success: Found user.",
            "DEBUG",
            user=active_user_read_only.id,
        )

    def test_not_found(self, superuser_read_only, caplog_loguru):
        with pytest.raises(NotFound) as exc:
            TmsUserService.get_user_via_id(superuser_read_only, 99999)

        assert USER_DOES_NOT_EXIST == str(exc.value.detail)

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Not found: User does not exist.", "WARNING")

    def test_multiple_objects_returned(
        self, superuser_read_only, active_user, monkeypatch, caplog_loguru
    ):
        def mock_get(*args, **kwargs):
            raise MultipleObjectsReturned("Multiple users found")

        monkeypatch.setattr(TmsUser.objects, "get", mock_get)

        with pytest.raises(MultipleObjectsReturned) as exc:
            TmsUserService.get_user_via_id(superuser_read_only, active_user.id)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Critical: Multiple Users returned! Reason {exc.value}.",
            "CRITICAL",
        )

    def test_permission_denied(
        self, superuser_read_only, active_user_read_only, caplog_loguru, monkeypatch
    ):
        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda a, u: False)

        with pytest.raises(PermissionDenied) as exc:
            TmsUserService.get_user_via_id(superuser_read_only, active_user_read_only.id)

        assert PERMISSION_DENIED_TO_VIEW_USER == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Not allowed to view user.",
            "WARNING",
        )

    def test_is_efficient(self, superuser_read_only, active_user_read_only):
        with utils.CaptureQueriesContext(connection) as queries:
            TmsUserService.get_user_via_id(superuser_read_only, active_user_read_only.id)

        assert len(queries) <= 1
