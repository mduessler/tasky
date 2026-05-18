import pytest
from task.api.v1.permissions import TaskPermission
from tests.utils import DummyView, assert_log, build_request


@pytest.mark.django_db
class TestHasPermission:
    def test_request_user_is_not_authenticated(self, anonymous_user, caplog_loguru):
        req = build_request("get", anonymous_user)
        result = TaskPermission().has_permission(req, DummyView("list"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "User is not authenticated.",
            "WARNING",
        )

    def test_view_has_no_action(self, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner
        req = build_request("get", actor)
        result = TaskPermission().has_permission(req, object())

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission Denied: View has no attribute 'action'.", "ERROR")

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
    def test_action_create_allowed(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("post", actor)
        result = TaskPermission().has_permission(req, DummyView("create"))

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for action 'create': True",
            "DEBUG",
            action="create",
        )

    def test_action_create_not_allowed(self, superuser, request, caplog_loguru, monkeypatch):
        req = build_request("post", superuser)
        monkeypatch.setattr("task.policies.TaskPolicy.can_create", lambda *a, **k: False)

        result = TaskPermission().has_permission(req, DummyView("create"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Has permission for action 'create': False", "DEBUG", action="create"
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
    def test_action_list_allowed(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("get", actor)
        result = TaskPermission().has_permission(req, DummyView("list"))

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Has permission for action 'list': True", "DEBUG", action="list")

    def test_action_list_not_allowed(self, superuser, request, caplog_loguru, monkeypatch):
        req = build_request("get", superuser)
        monkeypatch.setattr("task.policies.TaskPolicy.can_access", lambda *a, **k: False)

        result = TaskPermission().has_permission(req, DummyView("list"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Has permission for action 'list': False", "DEBUG", action="list")

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
    def test_action_retrive_and_other(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("get", actor)
        result = TaskPermission().has_permission(req, DummyView("retrieve"))

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for action 'retrieve': True",
            "DEBUG",
            action="retrieve",
        )

    def test_action_retrieve_not_allowed(self, superuser, request, caplog_loguru, monkeypatch):
        req = build_request("get", superuser)
        monkeypatch.setattr("task.policies.TaskPolicy.can_access", lambda *a, **k: False)

        result = TaskPermission().has_permission(req, DummyView("retrieve"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for action 'retrieve': False",
            "DEBUG",
            action="retrieve",
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "superuser_is_not_member",
        ],
    )
    def test_action_membership_allowed(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("post", actor)
        result = TaskPermission().has_permission(req, DummyView("membership"))

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for action 'membership': True",
            "DEBUG",
            action="membership",
        )

    def test_action_membership_not_allowed(self, user_is_not_member, caplog_loguru, monkeypatch):
        actor, _ = user_is_not_member
        req = build_request("post", actor)
        monkeypatch.setattr("task.policies.TaskMembershipPolicy.can_access", lambda *a, **k: False)

        result = TaskPermission().has_permission(req, DummyView("membership"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for action 'membership': False",
            "DEBUG",
            action="membership",
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "superuser_is_not_member",
        ],
    )
    def test_action_memberships_allowed(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("get", actor)
        result = TaskPermission().has_permission(req, DummyView("memberships"))

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for action 'memberships': True",
            "DEBUG",
            action="memberships",
        )

    def test_action_memberships_not_allowed(
        self, user_is_not_member, request, caplog_loguru, monkeypatch
    ):
        actor, _ = user_is_not_member
        req = build_request("get", actor)
        monkeypatch.setattr("task.policies.TaskMembershipPolicy.can_access", lambda *a, **k: False)

        result = TaskPermission().has_permission(req, DummyView("memberships"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for action 'memberships': False",
            "DEBUG",
            action="memberships",
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "superuser_is_not_member",
        ],
    )
    def test_action_note_allowed(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("post", actor)
        result = TaskPermission().has_permission(req, DummyView("note"))

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Has permission for action 'note': True", "DEBUG", action="note")

    def test_action_note_not_allowed(
        self, user_is_not_member, request, caplog_loguru, monkeypatch
    ):
        actor, _ = user_is_not_member
        req = build_request("post", actor)
        monkeypatch.setattr("task.policies.TaskNotePolicy.can_access", lambda *a, **k: False)

        result = TaskPermission().has_permission(req, DummyView("note"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Has permission for action 'note': False", "DEBUG", action="note")

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "superuser_is_not_member",
        ],
    )
    def test_action_notes_allowed(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("get", actor)
        result = TaskPermission().has_permission(req, DummyView("notes"))

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Has permission for action 'notes': True", "DEBUG", action="notes")

    def test_action_notes_not_allowed(
        self, user_is_not_member, request, caplog_loguru, monkeypatch
    ):
        actor, _ = user_is_not_member
        req = build_request("get", actor)
        monkeypatch.setattr("task.policies.TaskNotePolicy.can_access", lambda *a, **k: False)

        result = TaskPermission().has_permission(req, DummyView("notes"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Has permission for action 'notes': False", "DEBUG", action="notes")

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
    def test_action_update_not_allowed(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("put", actor)
        result = TaskPermission().has_permission(req, DummyView("update"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Has permission for action 'update': False", "DEBUG", action="update"
        )
