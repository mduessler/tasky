import pytest
from task.policies import TaskPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanViewTasks:
    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "user_is_not_member",
        ],
    )
    def test_permission_denied(self, actor_fixture, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        result = TaskPolicy.can_view_tasks(actor)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission granted to view task of user: False.", "DEBUG")

    def test_permission_granted_superuser(self, superuser, caplog_loguru):
        result = TaskPolicy.can_view_tasks(superuser)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission granted to view all tasks: Actor is superuser.", "INFO")
