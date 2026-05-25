import pytest
from task.api.v1.permissions import TaskNotePermission
from tests.utils import DummyView, assert_log, build_request


@pytest.mark.django_db
class TestHasPermission:
    def test_request_user_is_not_authenticated(self, anonymous_user, caplog_loguru):
        req = build_request("get", anonymous_user)
        result = TaskNotePermission().has_permission(req, DummyView("list"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "User is not authenticated.", "WARNING")

    def test_view_has_no_action(self, member_is_owner_read_only, caplog_loguru):
        actor, _ = member_is_owner_read_only
        req = build_request("get", actor)
        result = TaskNotePermission().has_permission(req, object())

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
    def test_action_create_not_allowed(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("post", actor)
        result = TaskNotePermission().has_permission(req, DummyView("create"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for task note action 'create': False",
            "DEBUG",
            action="create",
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
    def test_action_update_is_not_allowed(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("put", actor)
        result = TaskNotePermission().has_permission(req, DummyView("update"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for task note action 'update': False",
            "DEBUG",
            action="update",
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "superuser_is_not_member_read_only",
        ],
    )
    def test_action_list_allowed(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("get", actor)
        result = TaskNotePermission().has_permission(req, DummyView("list"))

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for task note action 'list': True",
            "DEBUG",
            action="list",
        )

    def test_action_list_not_allowed(
        self, user_is_not_member_read_only, caplog_loguru, monkeypatch
    ):
        actor, _ = user_is_not_member_read_only
        req = build_request("get", actor)
        monkeypatch.setattr("task.policies.TaskNotePolicy.can_access", lambda *a, **k: False)

        result = TaskNotePermission().has_permission(req, DummyView("list"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for task note action 'list': False",
            "DEBUG",
            action="list",
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "superuser_is_not_member_read_only",
        ],
    )
    def test_action_retrive_and_other(self, actor_data, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("get", actor)
        result = TaskNotePermission().has_permission(req, DummyView("retrieve"))

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for task note action 'retrieve': True",
            "DEBUG",
            action="retrieve",
        )

    def test_action_retrieve_not_allowed(
        self, user_is_not_member_read_only, request, caplog_loguru, monkeypatch
    ):
        actor, _ = user_is_not_member_read_only
        req = build_request("get", actor)
        monkeypatch.setattr("task.policies.TaskNotePolicy.can_access", lambda *a, **k: False)

        result = TaskNotePermission().has_permission(req, DummyView("retrieve"))

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has permission for task note action 'retrieve': False",
            "DEBUG",
            action="retrieve",
        )
