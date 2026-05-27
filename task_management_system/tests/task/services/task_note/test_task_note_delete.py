import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection
from django.db.models import ProtectedError
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_DELETE_TASK_NOTE
from task.models import TaskNote
from task.policies import TaskNotePolicy
from task.services import TaskNoteService
from tests.utils import assert_log


@pytest.mark.django_db
class TestDelete:
    def test_success(self, member_is_owner, task_note, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner
        note_id = task_note.id

        monkeypatch.setattr(TaskNotePolicy, "can_delete", lambda *a, **k: True)

        TaskNoteService.delete(actor, task_note.id)

        assert TaskNote.objects.filter(pk=note_id).exists() is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Success: Task note deleted.",
            "DEBUG",
            task=task_note.task.id,
            note=note_id,
        )

    def test_permission_denied(self, member_is_owner, task_note, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner
        note_id = task_note.id

        monkeypatch.setattr(TaskNotePolicy, "can_delete", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskNoteService.delete(actor, task_note.id)
        assert PERMISSION_DENIED_TO_DELETE_TASK_NOTE == str(exc.value)
        assert TaskNote.objects.filter(pk=note_id).exists() is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor cannot delete task note.",
            "WARNING",
            task=task_note.task.id,
            note=note_id,
        )

    def test_protected_error(self, member_is_owner, task_note, caplog_loguru, monkeypatch):
        def mock_delete(self):
            raise ProtectedError("Error", {"protected"})

        actor, _ = member_is_owner
        note_id = task_note.id

        monkeypatch.setattr(TaskNotePolicy, "can_delete", lambda *a, **k: True)
        monkeypatch.setattr(TaskNote, "delete", mock_delete)

        with pytest.raises(ValidationError):
            TaskNoteService.delete(actor, task_note.id)
        assert TaskNote.objects.filter(pk=note_id).exists() is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Protected error: Task note deletion failed.",
            "ERROR",
            task=task_note.task.id,
            note=task_note.id,
        )

    def test_atomicity_on_error(self, member_is_owner, task_note, monkeypatch):
        def mock_delete(self):
            raise ProtectedError("Error", {"protected"})

        actor, _ = member_is_owner
        note_id = task_note.id

        monkeypatch.setattr(TaskNotePolicy, "can_delete", lambda *a, **k: True)
        monkeypatch.setattr(TaskNote, "delete", mock_delete)

        with pytest.raises(ValidationError):
            TaskNoteService.delete(actor, task_note.id)
        assert TaskNote.objects.filter(pk=note_id).exists() is True

    def test_is_efficient(self, member_is_owner, task_note, monkeypatch):
        actor, _ = member_is_owner

        monkeypatch.setattr(TaskNotePolicy, "can_delete", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskNoteService.delete(actor, task_note.id)
        assert len(queries) <= 5
