import pytest
from registration.api.v1.permissions import RegisterUserPermission
from tests.utils import DummyView, assert_log, build_request


@pytest.mark.django_db
class TestHasPermission:
    @pytest.mark.parametrize("method", ["delete", "get", "patch", "post", "put"])
    def test_user_is_authenticated(self, method, active_user, caplog_loguru):
        req = build_request(method, active_user)
        result = RegisterUserPermission().has_permission(req, DummyView())

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor is already authenticated.",
            "WARNING",
        )

    @pytest.mark.parametrize("method", ["options", "head"])
    @pytest.mark.parametrize("actor_data", ["active_user", "inactive_user"])
    def test_method_is_safe_user_authenticated(self, method, actor_data, request, caplog_loguru):
        actor = request.getfixturevalue(actor_data)
        req = build_request(method, actor)
        result = RegisterUserPermission().has_permission(req, DummyView())

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Request method in save methods.",
            "DEBUG",
        )

    @pytest.mark.parametrize("method", ["options", "head"])
    def test_method_is_sage_user_not_authenticated(self, method, anonymous_user, caplog_loguru):
        req = build_request(method, anonymous_user)
        result = RegisterUserPermission().has_permission(req, DummyView())

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Request method in save methods.",
            "DEBUG",
        )

    def post_is_allowed(self, anonymous_user, caplog_loguru):
        req = build_request("post", anonymous_user)
        result = RegisterUserPermission().has_permission(req, DummyView())

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Has permission to register a new user.",
            "DEBUG",
        )

    @pytest.mark.parametrize("method", ["delete", "get", "patch", "put"])
    def method_is_not_allowed(self, method, anonymous_user, caplog_loguru):
        req = build_request(method, anonymous_user)
        result = RegisterUserPermission().has_permission(req, DummyView())

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: This method is not allowed in this view.",
            "WARNING",
        )
