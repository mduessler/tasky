import pytest
from tests.utils import DummyView, assert_log, build_request
from user.api.v1.permissions import TmsUserPermission


@pytest.mark.django_db
class TestHasObjPermission:
    def test_no_action(self, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner
        req = build_request("get", actor)
        result = TmsUserPermission().has_object_permission(req, object(), actor)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission Denied: View has no attribute 'action'.", "ERROR")

    def test_retrieve_allowed(self, member_is_owner, member_is_member, caplog_loguru):
        actor, _ = member_is_owner
        user, _ = member_is_member

        req = build_request("get", actor)
        result = TmsUserPermission().has_object_permission(req, DummyView("retrieve"), user)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has user permission for action 'retrieve': True",
            "DEBUG",
            action="retrieve",
            user=user.id,
        )

    def test_retrieve_not_allowed(self, member_is_owner, user_is_not_member, caplog_loguru):
        actor, _ = member_is_owner
        user, _ = user_is_not_member

        req = build_request("get", actor)
        result = TmsUserPermission().has_object_permission(req, DummyView("retrieve"), user)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has user permission for action 'retrieve': False",
            "DEBUG",
            action="retrieve",
            user=user.id,
        )

    def test_destroy_allowed(self, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner

        req = build_request("delete", actor)
        result = TmsUserPermission().has_object_permission(req, DummyView("destroy"), actor)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has user permission for action 'destroy': True",
            "DEBUG",
            action="destroy",
            user=actor.id,
        )

    def test_destroy_not_allowed(self, member_is_member, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner
        user, _ = member_is_member

        req = build_request("delete", actor)
        result = TmsUserPermission().has_object_permission(req, DummyView("destroy"), user)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has user permission for action 'destroy': False",
            "DEBUG",
            action="destroy",
            user=user.id,
        )

    def test_partial_update_allowed(self, member_is_owner, user_is_not_member, caplog_loguru):
        actor, _ = member_is_owner
        user, _ = user_is_not_member

        req = build_request("patch", actor)
        result = TmsUserPermission().has_object_permission(req, DummyView("partial_update"), user)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has user permission for action 'partial_update': True",
            "DEBUG",
            action="partial_update",
            user=user.id,
        )

    def test_unknown_object_action(self, member_is_owner, member_is_member, caplog_loguru):
        actor, _ = member_is_owner
        user, _ = member_is_member

        req = build_request("get", actor)
        result = TmsUserPermission().has_object_permission(req, DummyView("invalid"), user)

        assert result is False

        log_record = caplog_loguru.records[-2]
        assert_log(
            log_record,
            "Permission Denied: Unrecognized action 'invalid'.",
            "CRITICAL",
            action="invalid",
            user=user.id,
        )
