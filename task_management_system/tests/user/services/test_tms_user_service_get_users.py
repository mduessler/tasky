import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.db.models import QuerySet
from django.test import utils
from tests.utils import assert_log
from user.errors import PERMISSION_DENIED_TO_VIEW_USER
from user.models import TmsUser
from user.policies import TmsUserPolicy
from user.services import TmsUserService


@pytest.mark.django_db
class TestGetUsers:
    def test_success(self, superuser, caplog_loguru):
        result = TmsUserService.get_users(superuser)

        assert isinstance(result, QuerySet)
        assert result.count() == TmsUser.objects.count()

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Allowed: Returning users.",
            "DEBUG",
            user=superuser.id,
        )

    def test_permission_denied(self, superuser, caplog_loguru, monkeypatch):
        monkeypatch.setattr(TmsUserPolicy, "can_view_users", lambda a: False)

        with pytest.raises(PermissionDenied) as exc:
            TmsUserService.get_users(superuser)

        assert PERMISSION_DENIED_TO_VIEW_USER == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Not allowed to view users.",
            "WARNING",
        )

    def test_is_efficient(self, superuser):
        with utils.CaptureQueriesContext(connection) as queries:
            TmsUserService.get_users(superuser)

        assert len(queries) <= 1
