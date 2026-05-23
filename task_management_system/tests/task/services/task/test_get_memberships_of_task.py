import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP
from task.models import TaskMembership
from task.policies import TaskPolicy
from task.services import TaskService
from tests.utils import assert_log


@pytest.mark.django_db
class TestGetMembershipsOfATask:
    def test_success(self, member_is_owner_read_only, task_read_only, caplog_loguru, monkeypatch):
        cnt = TaskMembership.object.filter(task=task_read_only).count()
        monkeypatch.setattr(TaskPolicy, "can_view_memberships_of_task", lambda *a, **k: True)

        actor, _ = member_is_owner_read_only
        result = TaskService.get_memberships_of_task(actor, task_read_only)

        assert result.count() == cnt

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor can view task memberships.",
            "DEBUG",
            task=task_read_only.id,
        )

    def test_permission_denied(
        self, member_is_owner_read_only, task_read_only, caplog_loguru, monkeypatch
    ):
        actor, _ = member_is_owner_read_only

        monkeypatch.setattr(TaskPolicy, "can_view_memberships_of_task", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskService.get_memberships_of_task(actor, task_read_only)
        assert PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor cannot view task memberships.",
            "WARNING",
            task=task_read_only.id,
        )

    def test_is_efficient(self, member_is_owner_read_only, task_read_only, monkeypatch):
        actor, _ = member_is_owner_read_only

        monkeypatch.setattr(TaskPolicy, "can_view_memberships_of_task", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskService.get_memberships_of_task(actor, task_read_only)
        assert len(queries) <= 1
