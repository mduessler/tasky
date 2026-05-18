import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection
from django.db.models.deletion import ProtectedError
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_DELETE_TASK
from task.models import Task
from task.policies import TaskPolicy
from task.services import TaskService
from tests.utils import assert_log


@pytest.mark.django_db
class TestDelete:
    def test_success(self, member_is_owner, task, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner
        task_id = task.id

        monkeypatch.setattr(TaskPolicy, "can_delete", lambda *a, **k: True)

        TaskService.delete(actor, task.id)

        assert Task.objects.filter(id=task_id).exists() is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Success: Task deleted.", "DEBUG", task=task_id)

    def test_permission_denied(self, user_is_not_member, task, caplog_loguru, monkeypatch):
        actor, _ = user_is_not_member
        task_id = task.id

        monkeypatch.setattr(TaskPolicy, "can_delete", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskService.delete(actor, task.id)
        assert PERMISSION_DENIED_TO_DELETE_TASK == str(exc.value)
        assert Task.objects.filter(id=task_id).exists() is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Permission denied: Actor cannot delete the tasks", "WARNING", task=task_id
        )

    def test_protected_error(self, member_is_owner, task, caplog_loguru, monkeypatch):
        def mock_delete(self):
            raise ProtectedError("Error", Task.objects.none())

        actor, _ = member_is_owner
        task_id = task.id

        monkeypatch.setattr(TaskPolicy, "can_delete", lambda *a, **k: True)
        monkeypatch.setattr(Task, "delete", mock_delete)

        with pytest.raises(ValidationError):
            TaskService.delete(actor, task.id)
        assert Task.objects.filter(id=task_id).exists() is True

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Protected error: Task deletion failed.", "ERROR", task=task_id)

    def test_atomicity_on_error(self, member_is_owner, task, monkeypatch):
        def mock_delete(self):
            raise ProtectedError("Error", {"protected"})

        actor, _ = member_is_owner
        task_id = task.id

        monkeypatch.setattr(TaskPolicy, "can_delete", lambda *a, **k: True)
        monkeypatch.setattr(Task, "delete", mock_delete)

        with pytest.raises(ValidationError):
            TaskService.delete(actor, task.id)
        assert Task.objects.filter(pk=task_id).exists() is True

    def test_is_efficient(self, member_is_owner, task, monkeypatch):
        actor, _ = member_is_owner

        monkeypatch.setattr(TaskPolicy, "can_delete", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskService.delete(actor, task.id)
        assert len(queries) <= 6
