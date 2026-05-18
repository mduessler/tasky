import pytest
from tests.utils import assert_log
from user.permissions import TmsUserPermission
from user.policies import TmsUserPolicy


@pytest.mark.django_db
class TestGetEditableFields:
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
    def test_actor_is_user(self, actor_fixture, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        result = TmsUserPolicy.get_editable_fields(actor, actor)

        assert result == TmsUserPermission.get_update_permission("self")

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Getting update permission for 'self'.", "DEBUG", user=actor.id)

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
    def test_actor_is_superuser(self, superuser, user_fixture, request, caplog_loguru):
        user, _ = request.getfixturevalue(user_fixture)
        result = TmsUserPolicy.get_editable_fields(superuser, user)

        assert result == TmsUserPermission.get_update_permission("superuser")

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Getting update permission for 'superuser'.", "DEBUG", user=user.id)

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
        ],
    )
    @pytest.mark.parametrize(
        "user_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
        ],
    )
    def test_user_is_task_member(self, actor_fixture, user_fixture, request, caplog_loguru):
        if actor_fixture == user_fixture:
            return

        actor, _ = request.getfixturevalue(actor_fixture)
        user, _ = request.getfixturevalue(user_fixture)
        result = TmsUserPolicy.get_editable_fields(actor, user)

        assert result == TmsUserPermission.get_update_permission("group-member")

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Getting update permission for 'group-member'.", "DEBUG", user=user.id
        )

    @pytest.mark.parametrize(
        "user_fixture",
        [
            "member_is_owner",
            "member_is_member",
            "member_is_viewer",
        ],
    )
    def test_user_is_other(self, user_fixture, user_is_not_member, request, caplog_loguru):
        user, _ = request.getfixturevalue(user_fixture)
        actor, _ = user_is_not_member
        result = TmsUserPolicy.get_editable_fields(actor, user)

        assert result == TmsUserPermission.get_update_permission("other")

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Getting update permission for 'other'.", "DEBUG", user=user.id)
