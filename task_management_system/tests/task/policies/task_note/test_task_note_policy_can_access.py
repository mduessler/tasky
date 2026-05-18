import pytest
from task.models import TaskMembership
from task.policies import TaskNotePolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanAccess:
    @pytest.mark.parametrize(
        "actor_fixture",
        ["member_is_owner", "member_is_admin", "member_is_member", "member_is_viewer"],
    )
    def test_permission_granted(self, actor_fixture, task_notes, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        result = TaskNotePolicy.can_access(actor)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Permission granted: User is allowed to access task notes.", "DEBUG"
        )

    def test_has_permission_to_create_true_superuser(self, superuser, caplog_loguru):
        result = TaskNotePolicy.can_access(superuser)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser and has permission to access notes.",
            "INFO",
        )

    def test_no_task_memberships(self, user_is_not_member, caplog_loguru):
        actor, _ = user_is_not_member
        TaskMembership.objects.filter(user=actor).delete()
        result = TaskNotePolicy.can_access(actor)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Permission denied: User is not allowed to access task notes.", "DEBUG"
        )

    def test_anonymous_user(self, anonymous_user, caplog_loguru):
        result = TaskNotePolicy.can_access(anonymous_user)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User is not allowed to access task notes.",
            "WARNING",
        )

    def test_user_is_None(self, caplog_loguru):
        result = TaskNotePolicy.can_access(None)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User is not allowed to access task notes.",
            "WARNING",
        )
