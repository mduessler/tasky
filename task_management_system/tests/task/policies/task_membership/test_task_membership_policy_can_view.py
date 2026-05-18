import pytest
from django.db import connection
from django.test import utils
from task.models import Role, TaskMembership
from task.policies import TaskMembershipPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanView:
    @pytest.mark.parametrize(
        "actor_fixture",
        ["member_is_owner", "member_is_admin", "member_is_member", "member_is_viewer"],
    )
    def test_permission_granted_allowed_roles(
        self, actor_fixture, request, user_is_not_member, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        user, _ = user_is_not_member
        membership = TaskMembership.objects.create(
            task=actor_membership.task, user=user, role=Role.MEMBER
        )
        membership.refresh_from_db()

        result = TaskMembershipPolicy.can_view(actor, membership)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission to view membership: True.",
            "DEBUG",
            membership=membership.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_granted_superuser(self, superuser, member_is_viewer, caplog_loguru):
        _, membership = member_is_viewer
        result = TaskMembershipPolicy.can_view(superuser, membership)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser and can view membership.",
            "INFO",
            membership=membership.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        ["member_is_owner", "member_is_admin", "member_is_member", "member_is_viewer"],
    )
    def test_permission_granted_user_can_watch_own_membership(
        self, actor_fixture, request, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)

        result = TaskMembershipPolicy.can_view(actor, actor_membership)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: User can view it's own membership.",
            "DEBUG",
            membership=actor_membership.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_denied_user_has_no_membership(
        self, user_is_not_member, member_is_viewer, caplog_loguru
    ):
        actor, _ = user_is_not_member
        _, membership = member_is_viewer
        result = TaskMembershipPolicy.can_view(actor, membership)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor has no membership to view the membership.",
            "WARNING",
            membership=membership.id,
        )

    def test_denied_unsupported_future_role(
        self, member_is_owner, member_is_viewer, caplog_loguru
    ):
        actor, actor_membership = member_is_owner
        _, membership = member_is_viewer
        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")

        with pytest.raises(RuntimeError):
            TaskMembershipPolicy.can_view(actor, membership)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No view_permissions defined for role 'non-role' in "
            "TaskMembershipPermissions. Reason: 'non-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_owner, member_is_viewer, task_memberships):
        actor, _ = member_is_owner
        _, membership = member_is_viewer

        with utils.CaptureQueriesContext(connection) as queries:
            TaskMembershipPolicy.can_view(actor, membership)

        assert len(queries) <= 2
