import pytest
from django.db import connection
from django.test import utils
from task.models import TaskMembership
from task.policies import TaskMembershipPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanCreate:
    @pytest.mark.parametrize(
        "actor_fixture", ["member_is_owner_read_only", "member_is_admin_read_only"]
    )
    def test_permission_granted_allowed_roles(
        self, actor_fixture, request, task_read_only, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskMembershipPolicy.can_create(actor, task_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to create membership: True.",
            "DEBUG",
            task=task_read_only.id,
            actor_membership=actor_membership.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture", ["member_is_member_read_only", "member_is_viewer_read_only"]
    )
    def test_permission_denied_disallowed_roles(
        self, actor_fixture, request, task_read_only, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskMembershipPolicy.can_create(actor, actor_membership.task)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to create membership: False.",
            "DEBUG",
            task=task_read_only.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_granted_superuser(
        self, superuser_read_only, task_read_only, caplog_loguru
    ):
        result = TaskMembershipPolicy.can_create(superuser_read_only, task_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to create membership: Actor is superuser.",
            "INFO",
            task=task_read_only.id,
        )

    def test_permission_denied_user_has_no_membership(
        self, user_is_not_member_read_only, task_read_only, caplog_loguru
    ):
        actor, _ = user_is_not_member_read_only
        result = TaskMembershipPolicy.can_create(actor, task_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor has no membership to create a task membership.",
            "WARNING",
            task=task_read_only.id,
        )

    def test_denied_unsupported_future_role(
        self, member_is_owner_read_only, task_read_only, caplog_loguru
    ):
        actor, actor_membership = member_is_owner_read_only

        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")
        actor_membership.refresh_from_db()

        with pytest.raises(RuntimeError):
            TaskMembershipPolicy.can_create(actor, task_read_only)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No create_permissions defined for role 'non-role' "
            "in TaskMembershipPermissions. Reason: 'non-role'",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_owner_read_only, task_read_only):
        actor, _ = member_is_owner_read_only

        with utils.CaptureQueriesContext(connection) as queries:
            TaskMembershipPolicy.can_create(actor, task_read_only)
        assert len(queries) <= 2
