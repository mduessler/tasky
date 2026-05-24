import pytest
from tests.utils import assert_log
from user.policies import TmsUserPolicy


@pytest.mark.django_db
class TestCanViewUsers:
    def test_superuser_can_view_users(self, superuser_read_only, caplog_loguru):
        result = TmsUserPolicy.can_view_users(superuser_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser and can view user.",
            "INFO",
            user=superuser_read_only.id,
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
