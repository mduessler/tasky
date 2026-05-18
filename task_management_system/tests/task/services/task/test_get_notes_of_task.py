import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_VIEW_TASK_NOTE
from task.models import TaskNote
from task.policies import TaskPolicy
from task.services import TaskService
from tests.utils import assert_log


@pytest.mark.django_db
class TestGetNotes:
    def test_success(self, member_is_owner, task, task_notes, caplog_loguru, monkeypatch):
        monkeypatch.setattr(TaskPolicy, "can_view_notes_of_task", lambda *a, **k: True)

        actor, _ = member_is_owner
        notes = TaskService.get_notes_of_task(actor, task)

        assert notes.count() == TaskNote.objects.filter(task=task).count()

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Success: Getting notes of task.", "DEBUG", task=task.id)

    def test_permission_denied(self, member_is_owner, task, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner

        monkeypatch.setattr(TaskPolicy, "can_view_notes_of_task", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskService.get_notes_of_task(actor, task)
        assert PERMISSION_DENIED_TO_VIEW_TASK_NOTE == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor cannot view this task notes.",
            "WARNING",
            task=task.id,
        )

    def test_is_efficient(self, member_is_owner, task, monkeypatch):
        actor, _ = member_is_owner

        monkeypatch.setattr(TaskPolicy, "can_view_notes_of_task", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskService.get_notes_of_task(actor, task)
        assert len(queries) <= 2
