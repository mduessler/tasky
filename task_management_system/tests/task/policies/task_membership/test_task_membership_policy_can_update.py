import pytest
from django.db import connection
from django.test import utils
from task.models import TaskMembership
from task.policies import TaskMembershipPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanUpdate:
    def test_permission_granted_superuser(self, superuser, member_is_member, caplog_loguru):
        _, membership = member_is_member
        result = TaskMembershipPolicy.can_update(superuser, membership, {"any_field"})

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete membership: Actor is superuser.",
            "INFO",
            task=membership.task.id,
            membership=membership.id,
        )

    def test_owner_allowed_fields(self, member_is_owner, member_is_member, caplog_loguru):
        actor, actor_membership = member_is_owner
        _, membership = member_is_member

        result = TaskMembershipPolicy.can_update(actor, membership, {"role"})

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to update membership: True.",
            "DEBUG",
            task=membership.task.id,
            actor_membership=actor_membership.id,
            membership=membership.id,
        )

    def test_owner_denied_restricted_fields(
        self, member_is_owner, member_is_member, caplog_loguru
    ):
        actor, actor_membership = member_is_owner
        _, membership = member_is_member
        requested = {"user", "task"}

        result = TaskMembershipPolicy.can_update(actor, membership, requested)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor attempted to update membership restricted fields: "
            f"{requested - {'role'}}",
            "WARNING",
            task=membership.task.id,
            actor_membership=actor_membership.id,
            membership=membership.id,
        )

    def test_admin_allowed_fields(self, member_is_admin, member_is_member, caplog_loguru):
        actor, actor_membership = member_is_admin
        _, membership = member_is_member
        result = TaskMembershipPolicy.can_update(actor, membership, {"role"})

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to update membership: True.",
            "DEBUG",
            task=membership.task.id,
            actor_membership=actor_membership.id,
            membership=membership.id,
        )

    @pytest.mark.parametrize("role_fixture", ["member_is_member", "member_is_viewer"])
    def test_permission_denied_disallowed_roles(
        self, role_fixture, request, member_is_owner, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(role_fixture)
        _, membership = member_is_owner
        result = TaskMembershipPolicy.can_update(actor, membership, {"role"})

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to update membership: False.",
            "DEBUG",
            task=membership.task.id,
            actor_membership=actor_membership.id,
            membership=membership.id,
        )

    def test_denied_unsupported_future_role(
        self, member_is_owner, member_is_viewer, caplog_loguru
    ):
        actor, actor_membership = member_is_owner
        _, membership = member_is_viewer
        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")

        with pytest.raises(RuntimeError):
            TaskMembershipPolicy.can_update(actor, membership, {"role"})

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No update_permissions defined for role 'non-role' "
            "in TaskMembershipPermissions. Reason: 'non-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_owner, member_is_viewer):
        actor, _ = member_is_owner
        _, membership = member_is_viewer

        with utils.CaptureQueriesContext(connection) as queries:
            TaskMembershipPolicy.can_update(actor, membership, {"role"})

        assert len(queries) <= 2
