import pytest
from tests.utils import assert_log
from user.permissions import TmsUserPermission
from user.policies import TmsUserPolicy


@pytest.mark.django_db
class TestCanUpdate:
    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "superuser_is_not_member",
            "user_is_not_member",
        ],
    )
    def test_actor_is_user_valid_fields(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        result = TmsUserPolicy.can_update(
            actor, actor, TmsUserPermission.get_update_permission("self")
        )

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: User can update itself True.",
            "DEBUG",
            user=actor.id,
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "superuser_is_not_member",
            "user_is_not_member",
        ],
    )
    def test_actor_is_user_invalid_fields(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        result = TmsUserPolicy.can_update(actor, actor, {"invalid-field"})

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: User can update itself False.",
            "DEBUG",
            user=actor.id,
        )

    @pytest.mark.parametrize(
        "user_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "user_is_not_member",
        ],
    )
    def test_actor_is_superuser_valid_fields(
        self, superuser, user_fixture, request, caplog_loguru
    ):
        user, _ = request.getfixturevalue(user_fixture)
        result = TmsUserPolicy.can_update(
            superuser, user, TmsUserPermission.get_update_permission("superuser")
        )

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser and can update user True.",
            "INFO",
            user=user.id,
        )

    @pytest.mark.parametrize(
        "user_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "user_is_not_member",
        ],
    )
    def test_actor_is_superuser_invalid_fields(
        self, superuser, user_fixture, request, caplog_loguru
    ):
        user, _ = request.getfixturevalue(user_fixture)
        result = TmsUserPolicy.can_update(superuser, user, {"invalid-field"})

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser and can update user False.",
            "INFO",
            user=user.id,
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "user_is_not_member",
        ],
    )
    @pytest.mark.parametrize(
        "user_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "user_is_not_member",
        ],
    )
    def test_can_not_update_non_empty_fields(
        self, actor_data, user_fixture, request, caplog_loguru
    ):
        if actor_data == user_fixture:
            return

        actor, _ = request.getfixturevalue(actor_data)
        user, _ = request.getfixturevalue(user_fixture)
        result = TmsUserPolicy.can_update(
            actor, user, TmsUserPermission.get_update_permission("superuser")
        )

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor is not allowed to delete user False.",
            "DEBUG",
            user=user.id,
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "user_is_not_member",
        ],
    )
    @pytest.mark.parametrize(
        "user_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "user_is_not_member",
        ],
    )
    def test_can_not_update_empty_fields(self, actor_data, user_fixture, request, caplog_loguru):
        if actor_data == user_fixture:
            return

        actor, _ = request.getfixturevalue(actor_data)
        user, _ = request.getfixturevalue(user_fixture)
        result = TmsUserPolicy.can_update(actor, user, set())

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor is not allowed to delete user False.",
            "DEBUG",
            user=user.id,
        )
