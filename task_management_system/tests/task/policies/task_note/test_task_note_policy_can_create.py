import pytest
from django.db import connection
from django.test import utils
from task.models import TaskMembership
from task.policies import TaskNotePolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanCreate:
    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
        ],
    )
    def test_permission_granted_member(
        self, actor_fixture, request, task, task_memberships, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskNotePolicy.can_create(actor, task)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to create task note: True.",
            "DEBUG",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_granted_superuser(self, superuser, task, task_memberships, caplog_loguru):
        result = TaskNotePolicy.can_create(superuser, task)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser.",
            "INFO",
            task=task.id,
        )

    def test_permission_denied(self, member_is_viewer, task, task_memberships, caplog_loguru):
        actor, actor_membership = member_is_viewer
        result = TaskNotePolicy.can_create(actor, task)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to create task note: False.",
            "DEBUG",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_denied_no_membership(
        self, user_is_not_member, task, task_memberships, caplog_loguru
    ):
        actor, _ = user_is_not_member
        result = TaskNotePolicy.can_create(actor, task)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User has no membership for task.",
            "WARNING",
            task=task.id,
        )

    def test_denied_unsupported_future_role(
        self, member_is_owner, task, task_memberships, caplog_loguru
    ):
        actor, actor_membership = member_is_owner
        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")

        with pytest.raises(RuntimeError):
            TaskNotePolicy.can_create(actor, task)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No create_permissions defined for role 'non-role' "
            "in TaskNotePermissions. Reason: 'non-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_viewer, task, task_memberships):
        actor, _ = member_is_viewer

        with utils.CaptureQueriesContext(connection) as queries:
            TaskNotePolicy.can_create(actor, task)

        assert len(queries) <= 2
