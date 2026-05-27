import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_CREATE_TASK_NOTE
from task.models import TaskNote
from task.policies import TaskNotePolicy
from task.services import TaskNoteService
from tests.utils import assert_log


@pytest.mark.django_db
class TestCreate:
    def test_success(self, member_is_owner, task, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner
        note_data = {"note": "This is an important note", "task": task, "author": actor}
        note = TaskNoteService.create(actor, note_data)

        monkeypatch.setattr(TaskNotePolicy, "can_create", lambda *a, **k: True)

        db_note = TaskNote.objects.get(pk=note.id)

        assert note.id is not None
        assert db_note.note == "This is an important note"
        assert db_note.task == task
        assert db_note.author == actor

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Success: Task note created.", "DEBUG", task=task.id)

    def test_permission_denied(self, member_is_owner, task, caplog_loguru, monkeypatch):
        cnt = TaskNote.objects.count()
        actor, _ = member_is_owner
        note_data = {"note": "This is an important note", "task": task, "author": actor}

        monkeypatch.setattr(TaskNotePolicy, "can_create", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskNoteService.create(actor, note_data)
        assert PERMISSION_DENIED_TO_CREATE_TASK_NOTE == str(exc.value)
        assert TaskNote.objects.count() == cnt

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor cannot create task note.",
            "WARNING",
            task=task.id,
        )

    def test_validation_error(self, member_is_owner, task, caplog_loguru, monkeypatch):
        cnt = TaskNote.objects.count()

        def mock_full_clean(self, *a, **k):
            raise ValidationError("Error")

        actor, _ = member_is_owner
        note_data = {"note": "", "task": task, "author": actor}

        monkeypatch.setattr(TaskNotePolicy, "can_create", lambda *a, **k: True)
        monkeypatch.setattr(TaskNote, "full_clean", mock_full_clean)

        with pytest.raises(ValidationError) as exc:
            TaskNoteService.create(actor, note_data)
        assert TaskNote.objects.count() == cnt

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: can not create task note. Reason: {exc.value}",
            "WARNING",
            task=task.id,
        )

    def test_integrity_error(self, member_is_owner, task, caplog_loguru, monkeypatch):
        cnt = TaskNote.objects.count()

        def mock_save(self, *a, **k):
            raise IntegrityError("Error")

        actor, _ = member_is_owner
        note_data = {"note": "This is an important note", "task": task, "author": actor}

        monkeypatch.setattr(TaskNotePolicy, "can_create", lambda *a, **k: True)
        monkeypatch.setattr(TaskNote, "save", mock_save)

        with pytest.raises(IntegrityError) as exc:
            TaskNoteService.create(actor, note_data)
        assert TaskNote.objects.count() == cnt

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: can not create task note. Reason: {exc.value}",
            "WARNING",
            task=task.id,
        )

    def test_atomicity_on_error(self, member_is_owner, task, monkeypatch):
        def mock_save(self, *a, **k):
            raise IntegrityError("Error")

        cnt = TaskNote.objects.count()
        actor, _ = member_is_owner
        note_data = {"note": "This is an important note", "task": task, "author": actor}

        monkeypatch.setattr(TaskNotePolicy, "can_create", lambda *a, **k: True)
        monkeypatch.setattr(TaskNote, "save", mock_save)

        with pytest.raises(IntegrityError):
            TaskNoteService.create(actor, note_data)
        assert TaskNote.objects.count() == cnt

    def test_is_efficient(self, member_is_owner, task, monkeypatch):
        actor, _ = member_is_owner
        note_data = {"note": "This is an important note", "task": task, "author": actor}

        monkeypatch.setattr(TaskNotePolicy, "can_create", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskNoteService.create(actor, note_data)
        assert len(queries) <= 10
