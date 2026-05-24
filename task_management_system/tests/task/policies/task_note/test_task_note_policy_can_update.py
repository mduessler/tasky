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
class TestCanUpdate:
    @pytest.mark.parametrize(
        "actor_fixture", ["member_is_owner_read_only", "member_is_admin_read_only"]
    )
    def test_permission_granted_by_role(
        self, actor_fixture, request, task_note_read_only, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        task_note_read_only.created_at = timezone.now() - timedelta(hours=5)
        task_note_read_only.save()

        result = TaskNotePolicy.can_update(actor, task_note_read_only, {"note"})

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to update membership: True.",
            "DEBUG",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_granted_actor_is_author(
        self, member_is_owner_read_only, task_read_only, caplog_loguru
    ):
        actor, actor_membership = member_is_owner_read_only
        with freeze_time(timezone.now()):
            note = TaskNote.objects.create(
                note="A very important note", author=actor, task=task_read_only
            )
            result = TaskNotePolicy.can_update(actor, note, {"note"})
        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Can update own messages within 2 hours.",
            "DEBUG",
            task=task_read_only.task.id,
            note=task_read_only.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_granted_superuser(self, superuser, task_note_read_only, caplog_loguru):
        result = TaskNotePolicy.can_update(superuser, task_note_read_only, {"note"})

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser.",
            "INFO",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture", ["member_is_member_read_only", "member_is_viewer_read_only"]
    )
    def test_permission_denied_by_role(
        self, actor_fixture, request, task_note_read_only, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        task_note_read_only.created_at = timezone.now() - timedelta(hours=5)
        task_note_read_only.save()

        result = TaskNotePolicy.can_update(actor, task_note_read_only, {"note"})

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to update task note: False.",
            "DEBUG",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_denied_no_membership(
        self, user_is_not_member_read_only, task_note_read_only, caplog_loguru
    ):
        actor, _ = user_is_not_member_read_only
        result = TaskNotePolicy.can_update(actor, task_note_read_only, {"note"})

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User has no membership for task.",
            "WARNING",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
        )

    def test_permission_denied_actor_is_author_time_to_late(
        self, member_is_member_read_only, task_note_read_only, caplog_loguru
    ):
        actor, actor_membership = member_is_member_read_only

        with freeze_time(timezone.now() + timedelta(hours=3)):
            result = TaskNotePolicy.can_update(actor, task_note_read_only, {"note"})

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted to update task note: False.",
            "DEBUG",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
            actor_membership=actor_membership.id,
        )

    def test_permission_denied_restricted_fields(
        self, member_is_owner_read_only, task_note_read_only, caplog_loguru
    ):
        actor, actor_membership = member_is_owner_read_only
        requested_fields = {"note", "author_id"}

        result = TaskNotePolicy.can_update(actor, task_note_read_only, requested_fields)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor attempted to update membership restricted fields:"
            " {'author_id'}",
            "WARNING",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
            actor_membership=actor_membership.id,
        )

    def test_denied_unsupported_future_role(
        self, member_is_owner_read_only, task_note_read_only, caplog_loguru
    ):
        actor, actor_membership = member_is_owner_read_only
        task_note_read_only.created_at = timezone.now() - timedelta(hours=5)
        task_note_read_only.save()

        TaskMembership.objects.filter(pk=actor_membership.id).update(role="non-role")

        with pytest.raises(RuntimeError):
            TaskNotePolicy.can_update(actor, task_note_read_only, {"note"})

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Security Configuration Error: No update_permissions defined for role 'non-role' "
            "in TaskNotePermissions. Reason: 'non-role'.",
            "CRITICAL",
        )

    def test_is_efficient(self, member_is_owner_read_only, task_note_read_only):
        actor, _ = member_is_owner_read_only

        with utils.CaptureQueriesContext(connection) as queries:
            TaskNotePolicy.can_update(actor, task_note_read_only, {"note"})

        assert len(queries) <= 2
