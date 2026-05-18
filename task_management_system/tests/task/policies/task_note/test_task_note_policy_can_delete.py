from datetime import timedelta

import pytest
from django.db import connection
from django.test import utils
from django.utils import timezone
from freezegun import freeze_time
from task.models import TaskMembership, TaskNote
from task.policies import TaskNotePolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanDelete:
    @pytest.mark.parametrize("actor_fixture", ["member_is_owner", "member_is_admin"])
    def test_permission_granted_by_role(
        self, actor_fixture, request, expired_task_note, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskNotePolicy.can_delete(actor, expired_task_note)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete task note: True",
            "DEBUG",
            task=expired_task_note.task.id,
            note=expired_task_note.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_granted_actor_is_author(self, task_note, caplog_loguru):
        actor_membership = TaskMembership.objects.get(user=task_note.author, task=task_note.task)
        with freeze_time(timezone.now()):
            result = TaskNotePolicy.can_delete(task_note.author, task_note)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Can delete own messages within 2 hours.",
            "DEBUG",
            task=task_note.task_id,
            note=task_note.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_granted_superuser(self, superuser, task_note, caplog_loguru):
        result = TaskNotePolicy.can_delete(superuser, task_note)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser.",
            "INFO",
            task=task_note.task.id,
            note=task_note.id,
        )

    @pytest.mark.parametrize("actor_fixture", ["member_is_member", "member_is_viewer"])
    def test_permission_denied_by_role(
        self, actor_fixture, request, expired_task_note, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = TaskNotePolicy.can_delete(actor, expired_task_note)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete task note: False",
            "DEBUG",
            task=expired_task_note.task.id,
            note=expired_task_note.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_denied_no_membership(self, user_is_not_member, task_note, caplog_loguru):
        actor, _ = user_is_not_member
        TaskMembership.objects.filter(user=actor, task=task_note.task).delete()
        result = TaskNotePolicy.can_delete(actor, task_note)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User has no membership for task.",
            "WARNING",
            task=task_note.task.id,
            note=task_note.id,
        )

    def test_permission_denied_actor_is_author_time_to_late(
        self, member_is_member, task_note, caplog_loguru
    ):
        actor, actor_membership = member_is_member

        with freeze_time(timezone.now() + timedelta(20)):
            result = TaskNotePolicy.can_delete(actor, task_note)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to delete task note: False.",
            "DEBUG",
            task=task_note.task.id,
            note=task_note.id,
            actor_membership=actor_membership.id,
        )

    def test_denied_unsupported_future_role(self, member_is_owner, task_note, caplog_loguru):
        actor, actor_membership = member_is_owner
        TaskNote.objects.filter(pk=task_note.pk).update(
            created_at=timezone.now() - timedelta(hours=3)
        )
        task_note.refresh_from_db()

        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")

        with pytest.raises(RuntimeError):
            TaskNotePolicy.can_delete(actor, task_note)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No delete_permissions defined for role 'non-role' "
            "in TaskNotePermissions. Reason: 'non-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_owner, task_note):
        actor, _ = member_is_owner

        with utils.CaptureQueriesContext(connection) as queries:
            TaskNotePolicy.can_delete(actor, task_note)

        assert len(queries) <= 2
