import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.db.models import QuerySet
from django.test import utils
from task.models import TaskMembership
from tests.utils import assert_log
from user.errors import PERMISSION_DENIED_TO_VIEW_USER_TASK_MEMBERSHIPS
from user.policies import TmsUserPolicy
from user.services import TmsUserService


@pytest.mark.django_db
class TestGetUserMemberships:
    def test_success(self, member_is_owner, superuser, caplog_loguru, monkeypatch):
        user, _ = member_is_owner

        monkeypatch.setattr(TmsUserPolicy, "can_view_memberships_of_user", lambda a, u: True)

        result = TmsUserService.get_memberships_of_user(superuser, user.id)

        assert isinstance(result, QuerySet)
        assert result.count() == TaskMembership.objects.filter(user=user).count()

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Allowed: Returning task membership of user.",
            "DEBUG",
        )

    def test_permission_denied(self, member_is_owner, superuser, caplog_loguru, monkeypatch):
        user, _ = member_is_owner

        monkeypatch.setattr(TmsUserPolicy, "can_view_memberships_of_user", lambda a, u: False)

        with pytest.raises(PermissionDenied) as exc:
            TmsUserService.get_memberships_of_user(superuser, user.id)

        assert PERMISSION_DENIED_TO_VIEW_USER_TASK_MEMBERSHIPS == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Not allowed to view task memberships of user.",
            "WARNING",
        )

    def test_is_efficient(self, superuser, member_is_owner):
        user, _ = member_is_owner

        with utils.CaptureQueriesContext(connection) as queries:
            TmsUserService.get_memberships_of_user(superuser, user.id)

        assert len(queries) <= 1
