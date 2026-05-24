import pytest
from tests.utils import DummyView, assert_log, build_request
from user.api.v1.permissions import TmsUserPermission


@pytest.mark.django_db
class TestHasPermission:
    def test_action_options_allowed(self, superuser_read_only, caplog_loguru):
        req = build_request("options", superuser_read_only)
        result = TmsUserPermission().has_permission(req, DummyView("options"))

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for action 'metadata': True.",
            "DEBUG",
        )

    def test_request_user_is_not_authenticated(self, anonymous_user_read_only, caplog_loguru):
        req = build_request("get", anonymous_user_read_only)
        result = TmsUserPermission().has_permission(req, DummyView("list"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "User is not authenticated.",
            "WARNING",
        )

    def test_view_has_no_action(self, member_is_owner_read_only, caplog_loguru):
        actor, _ = member_is_owner_read_only
        req = build_request("get", actor)
        result = TmsUserPermission().has_permission(req, object())

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission Denied: View has no attribute 'action'.", "ERROR")

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "superuser_is_not_member_read_only",
            "user_is_not_member_read_only",
        ],
    )
    @pytest.mark.parametrize("action, method", [("create", "post"), ("update", "put")])
    def test_actions_not_allowed(self, actor_data, action, method, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request(method, actor)
        result = TmsUserPermission().has_permission(req, DummyView(action))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Has permission for action '{action}': False",
            "DEBUG",
            action=action,
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "superuser_is_not_member_read_only",
            "user_is_not_member_read_only",
        ],
    )
    @pytest.mark.parametrize(
        "action, method",
        [
            ("retrieve", "get"),
            ("list", "get"),
            ("partial_update", "patch"),
            ("destroy", "delete"),
        ],
    )
    def test_actions_allowed(self, actor_data, action, method, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request(method, actor)
        result = TmsUserPermission().has_permission(req, DummyView(action))

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Has permission for action '{action}': True",
            "DEBUG",
            action=action,
        )

    def test_unknown_action(self, superuser_is_not_member_read_only, caplog_loguru):
        actor, _ = superuser_is_not_member_read_only
        req = build_request("get", actor)
        result = TmsUserPermission().has_permission(req, DummyView("invalid"))

        assert result is False

        log_record = caplog_loguru.records[-2]
        assert_log(
            log_record,
            "Permission Denied: Unrecognized action 'invalid'.",
            "CRITICAL",
            action="invalid",
        )
