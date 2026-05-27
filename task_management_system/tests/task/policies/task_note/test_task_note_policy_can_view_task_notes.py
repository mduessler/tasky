import pytest
from task.policies import TaskNotePolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanViewAllTaskNotes:
    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_permission_denied(self, actor_fixture, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        result = TaskNotePolicy.can_view_task_notes(actor)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission granted to view all task notes: False.", "DEBUG")

    def test_permission_granted_superuser(self, superuser_read_only, caplog_loguru):
        result = TaskNotePolicy.can_view_task_notes(superuser_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to view all task notes: Actor is superuser.",
            "INFO",
        )
