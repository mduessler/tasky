import pytest
from tests.utils import assert_log
from user.policies import TmsUserPolicy


@pytest.mark.django_db
class TestCanView:
    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "superuser_is_not_member_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_actor_is_user(self, actor_fixture, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        result = TmsUserPolicy.can_view(actor, actor)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission granted: User can view itself.", "DEBUG", user=actor.id)

    @pytest.mark.parametrize(
        "user_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_actor_is_superuser(self, superuser_read_only, user_fixture, request, caplog_loguru):
        user, _ = request.getfixturevalue(user_fixture)
        result = TmsUserPolicy.can_view(superuser_read_only, user)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser and can view user.",
            "INFO",
            user=user.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
        ],
    )
    @pytest.mark.parametrize(
        "user_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
        ],
    )
    def test_share_the_same_task(self, actor_fixture, user_fixture, request, caplog_loguru):
        if actor_fixture == user_fixture:
            return

        actor, _ = request.getfixturevalue(actor_fixture)
        user, _ = request.getfixturevalue(user_fixture)
        result = TmsUserPolicy.can_view(actor, user)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor and user work on the same task.",
            "DEBUG",
            user=user.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        ["member_is_owner_read_only", "member_is_member_read_only", "member_is_viewer_read_only"],
    )
    def test_not_allowed(
        self, actor_fixture, user_is_not_member_read_only, request, caplog_loguru
    ):
        actor, _ = user_is_not_member_read_only
        user, _ = request.getfixturevalue(actor_fixture)
        result = TmsUserPolicy.can_view(actor, user)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor is not allowed to view user.",
            "DEBUG",
            user=user.id,
        )
