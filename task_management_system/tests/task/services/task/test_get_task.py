import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.test import utils
from rest_framework.exceptions import NotFound
from task.errors import PERMISSION_DENIED_TO_VIEW_TASK
from task.policies import TaskPolicy
from task.services import TaskService
from tests.utils import assert_log


@pytest.mark.django_db
class TestGetTask:
    def test_success(self, member_is_owner, task, caplog_loguru):
        actor, _ = member_is_owner
        retrieved_task = TaskService.get_task(actor, task.id)

        assert retrieved_task == task

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Permission granted: Actor can view this task.", "DEBUG", task=task.id
        )

    def test_not_found(self, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner
        non_existent_id = 9999

        with pytest.raises(NotFound):
            TaskService.get_task(actor, non_existent_id)

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Not found: Task not found.", "WARNING", task=non_existent_id)

    def test_permission_denied(self, user_is_not_member, task, caplog_loguru, monkeypatch):
        actor, _ = user_is_not_member

        monkeypatch.setattr(TaskPolicy, "can_view", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskService.get_task(actor, task.id)
        assert PERMISSION_DENIED_TO_VIEW_TASK == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Permission denied: Actor cannot view this task.", "WARNING", task=task.id
        )

    def test_is_efficient(self, member_is_owner, task):
        actor, _ = member_is_owner

        with utils.CaptureQueriesContext(connection) as queries:
            TaskService.get_task(actor, task.id)
        assert len(queries) <= 2
