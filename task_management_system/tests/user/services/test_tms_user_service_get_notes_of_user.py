import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.db.models import QuerySet
from django.test import utils
from task.models import TaskNote
from tests.utils import assert_log
from user.errors import PERMISSION_DENIED_TO_VIEW_USER_TASK_NOTES
from user.policies import TmsUserPolicy
from user.services import TmsUserService


@pytest.mark.django_db
class TestGetNotesOfUser:
    def test_success(
        self, member_is_owner_read_only, superuser_read_only, caplog_loguru, monkeypatch
    ):
        user, _ = member_is_owner_read_only

        monkeypatch.setattr(TmsUserPolicy, "can_view_notes_of_user", lambda a, u: True)

        result = TmsUserService.get_notes_of_user(superuser_read_only, user.id)

        assert isinstance(result, QuerySet)
        assert result.count() == TaskNote.objects.filter(author=user).count()

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Allowed: Returning task note of user.",
            "DEBUG",
        )

    def test_permission_denied(
        self, member_is_owner_read_only, superuser_read_only, caplog_loguru, monkeypatch
    ):
        user, _ = member_is_owner_read_only

        monkeypatch.setattr(TmsUserPolicy, "can_view_notes_of_user", lambda a, u: False)

        with pytest.raises(PermissionDenied) as exc:
            TmsUserService.get_notes_of_user(superuser_read_only, user.id)

        assert PERMISSION_DENIED_TO_VIEW_USER_TASK_NOTES == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Not allowed to view task notes of user.",
            "WARNING",
        )

    def test_is_efficient(self, superuser_read_only, member_is_owner_read_only):
        user, _ = member_is_owner_read_only

        with utils.CaptureQueriesContext(connection) as queries:
            TmsUserService.get_notes_of_user(superuser_read_only, user.id)

        assert len(queries) <= 1
