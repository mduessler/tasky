import pytest
from task.models import TaskMembership
from task.policies import TaskMembershipPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanAccess:
    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
        ],
    )
    def test_permission_granted(self, actor_fixture, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)

        result = TaskMembershipPolicy.can_access(actor)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Permission granted: User is allowed to access task memberships.", "DEBUG"
        )

    def test_has_permission_to_create_true_superuser(self, superuser_read_only, caplog_loguru):
        result = TaskMembershipPolicy.can_access(superuser_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser and has permission to access membership.",
            "INFO",
        )

    def test_no_task_memberships(self, user_is_not_member_read_only, caplog_loguru):
        actor, _ = user_is_not_member_read_only
        TaskMembership.objects.filter(user=actor).delete()

        result = TaskMembershipPolicy.can_access(actor)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Permission denied: User is not allowed to access task membersip.", "DEBUG"
        )

    def test_anonymous_user(self, anonymous_user_read_only, caplog_loguru):
        result = TaskMembershipPolicy.can_access(anonymous_user_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User is not allowed to access task membersip.",
            "WARNING",
        )

    def test_user_is_None(self, caplog_loguru):
        result = TaskMembershipPolicy.can_access(None)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User is not allowed to access task membersip.",
            "WARNING",
        )
