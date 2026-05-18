import pytest
from django.db import connection
from django.test import utils
from task.models import TaskMembership
from task.policies import TaskPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanUpdate:
    def test_permission_granted_superuser(self, superuser, task, caplog_loguru):
        result = TaskPolicy.can_update(superuser, task, {"any_field"})

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to update task: Actor is superuser.",
            "INFO",
            task=task.id,
        )

    def test_permission_denied_no_membership(self, user_is_not_member, task, caplog_loguru):
        actor, _ = user_is_not_member
        result = TaskPolicy.can_update(actor, task, {"status"})

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied to update task: User has no membership for task.",
            "WARNING",
            task=task.id,
        )

    def test_owner_allowed_fields(self, member_is_owner, task, caplog_loguru):
        actor, actor_membership = member_is_owner
        fields = {"title", "description", "status"}

        result = TaskPolicy.can_update(actor, task, fields)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to update task fields: True.",
            "DEBUG",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    def test_owner_denied_restricted_fields(self, member_is_owner, task, caplog_loguru):
        actor, actor_membership = member_is_owner
        requested = {"internal_note"}

        result = TaskPolicy.can_update(actor, task, requested)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: owner actor attempted to update restricted fields: "
            "{'internal_note'}.",
            "WARNING",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    def test_admin_allowed_fields(self, member_is_admin, task, caplog_loguru):
        actor, actor_membership = member_is_admin
        fields = {"status"}

        result = TaskPolicy.can_update(actor, task, fields)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to update task fields: True.",
            "DEBUG",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    def test_admin_denied_restricted_fields(self, member_is_admin, task, caplog_loguru):
        actor, actor_membership = member_is_admin
        requested = {"title"}

        result = TaskPolicy.can_update(actor, task, requested)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: admin actor attempted to update restricted fields: {'title'}.",
            "WARNING",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_denied_member_role(self, member_is_member, task, caplog_loguru):
        actor, actor_membership = member_is_member
        result = TaskPolicy.can_update(actor, task, {"status"})

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to update task: False.",
            "DEBUG",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_denied_viewer_role(self, member_is_viewer, task, caplog_loguru):
        actor, actor_membership = member_is_viewer
        result = TaskPolicy.can_update(actor, task, {"status"})

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to update task: False.",
            "DEBUG",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    def test_denies_unsupported_future_role(self, member_is_owner, task, caplog_loguru):
        actor, actor_membership = member_is_owner
        TaskMembership.objects.filter(pk=actor_membership.id).update(role="new-role")

        with pytest.raises(RuntimeError):
            TaskPolicy.can_update(actor, task, {"status"})

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No update_permissions defined for role 'new-role' "
            "in TaskPermissions. Reason: 'new-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_owner, task):
        actor, _ = member_is_owner

        with utils.CaptureQueriesContext(connection) as queries:
            TaskPolicy.can_update(actor, task, {"status"})

        assert len(queries) <= 1
