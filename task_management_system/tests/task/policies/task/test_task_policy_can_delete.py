import pytest
from django.db import connection
from django.test import utils
from task.models import TaskMembership
from task.policies import TaskPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanDelete:
    @pytest.mark.parametrize("actor_fixture", ["member_is_owner_read_only"])
    def test_permission_granted_role(self, actor_fixture, request, task_read_only, caplog_loguru):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskPolicy.can_delete(actor, task_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete task: True.",
            "DEBUG",
            task=task_read_only.id,
            actor_membership=actor_membership.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        ["member_is_admin_read_only", "member_is_member_read_only", "member_is_viewer_read_only"],
    )
    def test_permission_denied_role(self, actor_fixture, request, task_read_only, caplog_loguru):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskPolicy.can_delete(actor, task_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete task: False.",
            "DEBUG",
            task=task_read_only.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_denied_no_membership(
        self, user_is_not_member_read_only, task_read_only, caplog_loguru
    ):
        actor, _ = user_is_not_member_read_only
        result = TaskPolicy.can_delete(actor, task_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied to delete task: User has no membership for task.",
            "WARNING",
            task=task_read_only.id,
        )

    def test_permission_granted_superuser(
        self, superuser_read_only, task_read_only, caplog_loguru
    ):
        result = TaskPolicy.can_delete(superuser_read_only, task_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete task: Actor is superuser.",
            "INFO",
            task=task_read_only.id,
        )

    def test_denies_unsupported_future_role(
        self, member_is_owner_read_only, task_read_only, caplog_loguru
    ):
        actor, actor_membership = member_is_owner_read_only
        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")

        with pytest.raises(RuntimeError):
            TaskPolicy.can_delete(actor, task_read_only)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No delete_permissions defined for role 'non-role' "
            "in TaskPermissions. Reason: 'non-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_owner_read_only, task):
        actor, _ = member_is_owner_read_only

        with utils.CaptureQueriesContext(connection) as queries:
            TaskPolicy.can_delete(actor, task)

        assert len(queries) <= 1
