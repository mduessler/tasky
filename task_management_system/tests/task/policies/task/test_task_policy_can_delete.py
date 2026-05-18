import pytest
from django.db import connection
from django.test import utils
from task.models import TaskMembership
from task.policies import TaskPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanDelete:
    @pytest.mark.parametrize("actor_fixture", ["member_is_owner"])
    def test_permission_granted_role(self, actor_fixture, request, task, caplog_loguru):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskPolicy.can_delete(actor, task)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete task: True.",
            "DEBUG",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture", ["member_is_admin", "member_is_member", "member_is_viewer"]
    )
    def test_permission_denied_role(self, actor_fixture, request, task, caplog_loguru):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskPolicy.can_delete(actor, task)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete task: False.",
            "DEBUG",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_denied_no_membership(self, user_is_not_member, task, caplog_loguru):
        actor, _ = user_is_not_member
        result = TaskPolicy.can_delete(actor, task)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied to delete task: User has no membership for task.",
            "WARNING",
            task=task.id,
        )

    def test_permission_granted_superuser(self, superuser, task, caplog_loguru):
        result = TaskPolicy.can_delete(superuser, task)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete task: Actor is superuser.",
            "INFO",
            task=task.id,
        )

    def test_denies_unsupported_future_role(
        self, member_is_owner, task, task_memberships, caplog_loguru
    ):
        actor, actor_membership = member_is_owner
        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")

        with pytest.raises(RuntimeError):
            TaskPolicy.can_delete(actor, task)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No delete_permissions defined for role 'non-role' "
            "in TaskPermissions. Reason: 'non-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_owner, task):
        actor, _ = member_is_owner

        with utils.CaptureQueriesContext(connection) as queries:
            TaskPolicy.can_delete(actor, task)

        assert len(queries) <= 1
