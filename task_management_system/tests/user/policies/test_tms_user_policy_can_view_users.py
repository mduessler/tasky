import pytest
from tests.utils import assert_log
from user.policies import TmsUserPolicy


@pytest.mark.django_db
class TestCanViewUsers:
    def test_superuser_can_view_users(self, superuser, caplog_loguru):
        result = TmsUserPolicy.can_view_users(superuser)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser and can view user.",
            "INFO",
            user=superuser.id,
        )

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
    def test_user_can_not_view_users(self, actor_fixture, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        result = TmsUserPolicy.can_view_users(actor)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor is not allowed to view user.",
            "DEBUG",
            user=actor.id,
        )
