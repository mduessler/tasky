import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_VIEW_TASK
from task.models import Task
from task.policies import TaskPolicy
from task.services import TaskService
from tests.utils import assert_log


@pytest.mark.django_db
class TestGetTasks:
    def test_success(self, member_is_owner, tasks, caplog_loguru, monkeypatch):
        monkeypatch.setattr(TaskPolicy, "can_view_tasks", lambda *a, **k: True)

        actor, _ = member_is_owner
        result = TaskService.get_tasks(actor)

        assert result.count() == Task.objects.count()

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Tasks successfully retrieved with status None.",
            "DEBUG",
        )

    def test_success_filter_status(self, member_is_owner, tasks, caplog_loguru, monkeypatch):
        monkeypatch.setattr(TaskPolicy, "can_view_tasks", lambda *a, **k: True)

        actor, _ = member_is_owner
        result = TaskService.get_tasks(actor, status="todo")

        assert result.count() == Task.objects.filter(status="todo").count()

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Tasks successfully retrieved with status todo.",
            "DEBUG",
        )

    def test_success_empty_result(self, member_is_owner, tasks, caplog_loguru, monkeypatch):
        monkeypatch.setattr(TaskPolicy, "can_view_tasks", lambda *a, **k: True)

        actor, _ = member_is_owner
        result = TaskService.get_tasks(actor, status="non-existent")

        assert result.count() == 0

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Tasks successfully retrieved with status non-existent.",
            "DEBUG",
        )

    def test_permission_denied(self, member_is_owner, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner

        monkeypatch.setattr(TaskPolicy, "can_view_tasks", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskService.get_tasks(actor)

        assert PERMISSION_DENIED_TO_VIEW_TASK == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor cannot view tasks.",
            "WARNING",
        )

    def test_is_efficient(self, member_is_owner, tasks, monkeypatch):
        actor, _ = member_is_owner

        monkeypatch.setattr(TaskPolicy, "can_view_tasks", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskService.get_tasks(actor)
        assert len(queries) <= 1
