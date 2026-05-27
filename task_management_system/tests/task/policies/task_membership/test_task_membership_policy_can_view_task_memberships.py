import pytest
from task.policies import TaskMembershipPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanViewTaskMemberships:
    def test_permission_allowed_for_superuser(self, superuser_read_only, caplog_loguru):
        result = TaskMembershipPolicy.can_view_task_memberships(superuser_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Permission granted to view memberships: Actor is superuser.", "INFO"
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_permission_denied_for_all_roles(self, actor_fixture, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        result = TaskMembershipPolicy.can_view_task_memberships(actor)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Permission denied to view memberships: Actor is not superuser.", "DEBUG"
        )
