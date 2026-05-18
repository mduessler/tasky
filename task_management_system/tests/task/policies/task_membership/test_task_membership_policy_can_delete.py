import pytest
from django.db import connection
from django.test import utils
from task.models import TaskMembership
from task.policies import TaskMembershipPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanDelete:
    @pytest.mark.parametrize("actor_fixture", ["member_is_owner", "member_is_admin"])
    def test_permission_granted_allowed_roles(
        self, actor_fixture, request, member_is_viewer, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        _, membership = member_is_viewer
        result = TaskMembershipPolicy.can_delete(actor, membership)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete membership: True.",
            "DEBUG",
            task=membership.task.id,
            actor_membership=actor_membership.id,
            membership=membership.id,
        )

    @pytest.mark.parametrize("actor_fixture", ["member_is_member", "member_is_viewer"])
    def test_permission_denied_disallowed_roles(
        self, actor_fixture, request, member_is_owner, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        _, membership = member_is_owner
        result = TaskMembershipPolicy.can_delete(actor, membership)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete membership: False.",
            "DEBUG",
            task=membership.task.id,
            actor_membership=actor_membership.id,
            membership=membership.id,
        )

    def test_permission_granted_self_deletion(self, member_is_viewer, caplog_loguru):
        actor, actor_membership = member_is_viewer
        result = TaskMembershipPolicy.can_delete(actor, actor_membership)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete membership: User can delete it's own membership.",
            "DEBUG",
            task=actor_membership.task.id,
            actor_membership=actor_membership.id,
            membership=actor_membership.id,
        )

    def test_permission_granted_superuser(self, superuser, member_is_owner, caplog_loguru):
        _, membership = member_is_owner
        result = TaskMembershipPolicy.can_delete(superuser, membership)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete membership: Actor is superuser.",
            "INFO",
            task=membership.task.id,
            membership=membership.id,
        )

    def test_denied_unsupported_future_role(
        self, member_is_owner, member_is_viewer, caplog_loguru
    ):

        actor, actor_membership = member_is_owner
        _, membership = member_is_viewer
        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")

        with pytest.raises(RuntimeError):
            TaskMembershipPolicy.can_delete(actor, membership)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No delete_permissions defined for role 'non-role' "
            "in TaskMembershipPermissions. Reason: 'non-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_owner, member_is_viewer):
        actor, _ = member_is_owner
        _, membership = member_is_viewer
        with utils.CaptureQueriesContext(connection) as queries:
            TaskMembershipPolicy.can_delete(actor, membership)
        assert len(queries) <= 1
