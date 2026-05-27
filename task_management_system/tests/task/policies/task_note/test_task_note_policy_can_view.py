import pytest
from django.db import connection
from django.test import utils
from task.models import TaskMembership
from task.policies import TaskNotePolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanView:
    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
        ],
    )
    def test_permission_granted_member(
        self, actor_fixture, request, task_note_read_only, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskNotePolicy.can_view(actor, task_note_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to view task note: True",
            "DEBUG",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_granted_superuser(
        self, superuser_read_only, task_note_read_only, caplog_loguru
    ):
        result = TaskNotePolicy.can_view(superuser_read_only, task_note_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser.",
            "INFO",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
        )

    def test_permission_denied(
        self, user_is_not_member_read_only, task_note_read_only, caplog_loguru
    ):
        actor, _ = user_is_not_member_read_only
        result = TaskNotePolicy.can_view(actor, task_note_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User has no membership for task.",
            "WARNING",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
        )

    def test_denied_unsupported_future_role(
        self, member_is_owner_read_only, task_note_read_only, caplog_loguru
    ):
        actor, actor_membership = member_is_owner_read_only
        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")

        with pytest.raises(RuntimeError):
            TaskNotePolicy.can_view(actor, task_note_read_only)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No view_permissions defined for role 'non-role' "
            "in TaskNotePermissions. Reason: 'non-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_viewer_read_only, task_note):
        actor, _ = member_is_viewer_read_only

        with utils.CaptureQueriesContext(connection) as queries:
            TaskNotePolicy.can_view(actor, task_note)

        assert len(queries) <= 2
