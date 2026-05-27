import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.test import utils
from rest_framework.exceptions import NotFound
from task.errors import PERMISSION_DENIED_TO_VIEW_TASK_NOTE
from task.policies import TaskNotePolicy
from task.services import TaskNoteService
from tests.utils import assert_log


@pytest.mark.django_db
class TestGetNote:
    def test_success(
        self, member_is_owner_read_only, task_note_read_only, caplog_loguru, monkeypatch
    ):
        monkeypatch.setattr(TaskNotePolicy, "can_view", lambda *a, **k: True)

        actor, _ = member_is_owner_read_only
        note = TaskNoteService.get_task_note(actor, task_note_read_only.id)

        assert note.id == task_note_read_only.id

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor can view this task note.",
            "DEBUG",
            note=task_note_read_only.id,
            task=task_note_read_only.task_id,
        )

    def test_not_found(self, member_is_owner_read_only, caplog_loguru):
        actor, _ = member_is_owner_read_only
        invalid_id = 99999

        with pytest.raises(NotFound):
            TaskNoteService.get_task_note(actor, invalid_id)

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Not found: Task note not found.", "WARNING", note=invalid_id)

    def test_permission_denied(
        self, member_is_owner_read_only, task_note_read_only, caplog_loguru, monkeypatch
    ):
        actor, _ = member_is_owner_read_only

        monkeypatch.setattr(TaskNotePolicy, "can_view", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskNoteService.get_task_note(actor, task_note_read_only.id)
        assert PERMISSION_DENIED_TO_VIEW_TASK_NOTE == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor cannot view this task note.",
            "WARNING",
            note=task_note_read_only.id,
            task=task_note_read_only.task_id,
        )

    def test_is_efficient(self, member_is_owner_read_only, task_note_read_only, monkeypatch):
        actor, _ = member_is_owner_read_only

        monkeypatch.setattr(TaskNotePolicy, "can_view", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskNoteService.get_task_note(actor, task_note_read_only.id)
        assert len(queries) <= 3
