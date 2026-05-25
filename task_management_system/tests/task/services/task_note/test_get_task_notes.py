import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_VIEW_TASK_NOTE
from task.models import TaskNote
from task.services import TaskNoteService
from tests.utils import assert_log


@pytest.mark.django_db
class TestGetTaskNotes:
    def test_success(self, superuser_read_only, task_notes_read_only, caplog_loguru):
        notes = TaskNoteService.get_task_notes(superuser_read_only)

        assert notes.count() == TaskNote.objects.all().count()

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Success: Getting all task notes.", "DEBUG")

    def test_permission_denied(self, member_is_owner_read_only, caplog_loguru):
        actor, _ = member_is_owner_read_only
        with pytest.raises(PermissionDenied) as exc:
            TaskNoteService.get_task_notes(actor)
        assert PERMISSION_DENIED_TO_VIEW_TASK_NOTE == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission denied: Actor cannot view all task notes.", "WARNING")

    def test_is_efficient(self, superuser):
        with utils.CaptureQueriesContext(connection) as queries:
            TaskNoteService.get_task_notes(superuser)
        assert len(queries) <= 1
