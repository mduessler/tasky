import pytest
from tests.utils import assert_log
from user.policies import TmsUserPolicy


@pytest.mark.django_db
class TestCanViewUserMemberships:
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
    def test_user_can_view_own_memberships(self, actor_fixture, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        result = TmsUserPolicy.can_view_memberships_of_user(actor, actor)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: User can view it's own task memberships.",
            "DEBUG",
            user=actor.id,
        )

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
    def test_superuser_can_view_memberships_of_user(
        self, superuser_read_only, user_fixture, request, caplog_loguru
    ):
        user, _ = request.getfixturevalue(user_fixture)
        result = TmsUserPolicy.can_view_memberships_of_user(superuser_read_only, user)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser and can view user task memberships.",
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
            "user_is_not_member_read_only",
        ],
    )
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
    def test_user_can_not_view_other_user_memberships(
        self, actor_fixture, user_fixture, request, caplog_loguru
    ):
        if actor_fixture == user_fixture:
            return

        actor, _ = request.getfixturevalue(actor_fixture)
        user, _ = request.getfixturevalue(user_fixture)
        result = TmsUserPolicy.can_view_memberships_of_user(actor, user)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor is not allowed to view user memberships.",
            "DEBUG",
            user=user.id,
        )
