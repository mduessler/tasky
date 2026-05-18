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
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
        ],
    )
    def test_permission_granted_member(
        self, actor_fixture, request, task_note, task_memberships, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskNotePolicy.can_view(actor, task_note)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to view task note: True",
            "DEBUG",
            task=task_note.task.id,
            note=task_note.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_granted_superuser(
        self, superuser, task_note, task_memberships, caplog_loguru
    ):
        result = TaskNotePolicy.can_view(superuser, task_note)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser.",
            "INFO",
            task=task_note.task.id,
            note=task_note.id,
        )

    def test_permission_denied(
        self, user_is_not_member, task_note, task_memberships, caplog_loguru
    ):
        actor, _ = user_is_not_member
        result = TaskNotePolicy.can_view(actor, task_note)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User has no membership for task.",
            "WARNING",
            task=task_note.task.id,
            note=task_note.id,
        )

    def test_denied_unsupported_future_role(
        self, member_is_owner, task_note, task_memberships, caplog_loguru
    ):
        actor, actor_membership = member_is_owner
        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")

        with pytest.raises(RuntimeError):
            TaskNotePolicy.can_view(actor, task_note)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No view_permissions defined for role 'non-role' "
            "in TaskNotePermissions. Reason: 'non-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_viewer, task_note):
        actor, _ = member_is_viewer

        with utils.CaptureQueriesContext(connection) as queries:
            TaskNotePolicy.can_view(actor, task_note)

        assert len(queries) <= 2
