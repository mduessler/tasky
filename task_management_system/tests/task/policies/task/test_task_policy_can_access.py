import pytest
from task.policies import TaskPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestCanAccess:
    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "superuser_is_not_member",
            "user_is_not_member",
        ],
    )
    def test_tms_user(self, actor_fixture, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        result = TaskPolicy.can_access(actor)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission granted: User is allowed to access tasks.", "DEBUG")

    def test_anonymous_user(self, anonymous_user, caplog_loguru):
        result = TaskPolicy.can_access(anonymous_user)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission denied: User is not allowed to access task.", "DEBUG")

    def test_user_is_None(self, caplog_loguru):
        result = TaskPolicy.can_access(None)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission denied: User is not allowed to access task.", "DEBUG")
