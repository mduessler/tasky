import pytest
from django.db import connection
from django.test import utils
from task.models import TaskMembership
from task.policies import TaskPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanViewNotesOfTask:
    @pytest.mark.parametrize(
        "actor_fixture",
        ["member_is_owner", "member_is_admin", "member_is_member", "member_is_viewer"],
    )
    def test_notes_permission_granted_member(self, actor_fixture, request, task, caplog_loguru):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskPolicy.can_view_notes_of_task(actor, task)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to view notes of task: True.",
            "DEBUG",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    def test_notes_permission_granted_superuser(self, superuser, task, caplog_loguru):
        result = TaskPolicy.can_view_notes_of_task(superuser, task)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission granted: Actor is superuser.", "INFO", task=task.id)

    def test_notes_permission_denied_no_membership(self, user_is_not_member, task, caplog_loguru):
        actor, _ = user_is_not_member
        result = TaskPolicy.can_view_notes_of_task(actor, task)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User has no membership for task.",
            "WARNING",
            task=task.id,
        )

    def test_notes_denied_unsupported_future_role(self, member_is_owner, task, caplog_loguru):
        actor, actor_membership = member_is_owner
        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")

        with pytest.raises(RuntimeError):
            TaskPolicy.can_view_notes_of_task(actor, task)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No view_permissions defined for role 'non-role' "
            "in TaskNotePermissions. Reason: 'non-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_viewer, task):
        actor, _ = member_is_viewer

        with utils.CaptureQueriesContext(connection) as queries:
            TaskPolicy.can_view_notes_of_task(actor, task)

        assert len(queries) <= 2
