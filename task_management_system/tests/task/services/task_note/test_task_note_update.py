from unittest.mock import patch

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_UPDATE_TASK_NOTE
from task.models import TaskNote
from task.policies import TaskNotePolicy
from task.services import TaskNoteService
from tests.utils import assert_log


@pytest.mark.django_db
class TestUpdate:
    def test_success(self, member_is_owner, task_note, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner
        update_data = {"note": "This is an important note"}
        updated_note = TaskNoteService.update(actor, task_note.id, update_data)

        monkeypatch.setattr(TaskNotePolicy, "can_update", lambda *a, **k: True)

        task_note.refresh_from_db()
        assert updated_note.note == "This is an important note"
        assert updated_note.note == task_note.note

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Success: Task note updated.",
            "DEBUG",
            note=task_note.id,
            task=task_note.task_id,
        )

    def test_permission_denied(self, member_is_owner, task_note, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner
        update_data = {"note": "This is an important note"}

        monkeypatch.setattr(TaskNotePolicy, "can_update", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskNoteService.update(actor, task_note.id, update_data)
        assert PERMISSION_DENIED_TO_UPDATE_TASK_NOTE == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor cannot delete task note.",
            "WARNING",
            note=task_note.id,
            task=task_note.task_id,
        )

    def test_validation_error(self, member_is_owner, task_note, caplog_loguru, monkeypatch):
        def mock_full_clean(self):
            raise ValidationError("Error")

        actor, _ = member_is_owner
        update_data = {"note": ""}

        monkeypatch.setattr(TaskNotePolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TaskNote, "full_clean", mock_full_clean)

        with pytest.raises(ValidationError) as exc:
            TaskNoteService.update(actor, task_note.id, update_data)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: can not update task note. Reason: {exc.value}",
            "WARNING",
            note=task_note.id,
            task=task_note.task_id,
        )

    def test_integrity_error(self, member_is_owner, task_note, caplog_loguru, monkeypatch):
        def mock_save(self, update_fields=None):
            raise IntegrityError("Error")

        actor, _ = member_is_owner
        update_data = {"note": "This is an important note"}

        monkeypatch.setattr(TaskNotePolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TaskNote, "save", mock_save)

        with pytest.raises(IntegrityError) as exc:
            TaskNoteService.update(actor, task_note.id, update_data)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: can not update task note. Reason: {exc.value}",
            "WARNING",
            note=task_note.id,
            task=task_note.task_id,
        )

    def test_empty_data(self, member_is_owner, task_note, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner
        update_data = {}

        monkeypatch.setattr(TaskNotePolicy, "can_update", lambda *a, **k: True)

        with pytest.raises(ValidationError) as exc:
            TaskNoteService.update(actor, task_note.id, update_data)
        assert "Validation error: Task note update failed." == exc.value.messages[0]

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Validation error: Not allowed to update 0 fields.",
            "WARNING",
            note=task_note.id,
            task=task_note.task.id,
        )

    def test_partial_update_does_not_override_other_fields(
        self, member_is_owner, task_note, monkeypatch
    ):
        actor, _ = member_is_owner
        original_author = task_note.author

        monkeypatch.setattr(TaskNotePolicy, "can_update", lambda *a, **k: True)

        TaskNoteService.update(actor, task_note.id, {"note": "This is an important note"})

        task_note.refresh_from_db()
        assert task_note.note == "This is an important note"
        assert task_note.author == original_author

    @patch.object(TaskNote, "save")
    def test_update_fields_used_correctly(
        self, mock_save, member_is_owner, task_note, monkeypatch
    ):
        actor, _ = member_is_owner

        monkeypatch.setattr(TaskNotePolicy, "can_update", lambda *a, **k: True)

        TaskNoteService.update(actor, task_note.id, {"note": "This is an important note"})

        assert mock_save.call_args.kwargs["update_fields"] == ["note"]

    def test_atomicity_on_error(self, member_is_owner, task_note, monkeypatch):
        def mock_save(self, update_fields=None):
            raise IntegrityError("Error")

        actor, _ = member_is_owner
        original_note = task_note.note

        monkeypatch.setattr(TaskNotePolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TaskNote, "save", mock_save)

        with pytest.raises(IntegrityError):
            TaskNoteService.update(actor, task_note.id, {"note": "This is an important note"})

        task_note.refresh_from_db()
        assert task_note.note == original_note

    def test_is_efficient(self, member_is_owner, task_note, monkeypatch):
        actor, _ = member_is_owner
        update_data = {"note": "This is an important note"}

        monkeypatch.setattr(TaskNotePolicy, "can_update", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskNoteService.update(actor, task_note.id, update_data)
        assert len(queries) <= 12
