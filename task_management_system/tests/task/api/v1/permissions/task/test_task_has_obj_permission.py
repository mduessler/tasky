import pytest
from task.api.v1.permissions import TaskPermission
from tests.utils import DummyView, assert_log, build_request


@pytest.mark.django_db
class TestHasObjPermission:
    def test_view_has_no_action(self, member_is_owner_read_only, task_read_only, caplog_loguru):
        actor, _ = member_is_owner_read_only
        req = build_request("get", actor)
        result = TaskPermission().has_object_permission(req, object(), task_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission Denied: View has no attribute 'action'.", "ERROR")

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
    def test_action_create_is_not_allowed(
        self, actor_fixture, task_read_only, request, caplog_loguru
    ):
        actor, _ = request.getfixturevalue(actor_fixture)
        req = build_request("post", actor)
        result = TaskPermission().has_object_permission(req, DummyView("create"), task_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for action 'create': False",
            "DEBUG",
            action="create",
            task=task_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "superuser_is_not_member_read_only",
        ],
    )
    def test_action_retrieve_allowed(self, actor_fixture, task_read_only, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        req = build_request("get", actor)
        result = TaskPermission().has_object_permission(req, DummyView("retrieve"), task_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for action 'retrieve': True",
            "DEBUG",
            action="retrieve",
            task=task_read_only.id,
        )

    def test_action_retrieve_not_allowed(
        self, user_is_not_member_read_only, task_read_only, request, caplog_loguru
    ):
        actor, _ = user_is_not_member_read_only
        req = build_request("get", actor)
        result = TaskPermission().has_object_permission(req, DummyView("retrieve"), task_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for action 'retrieve': False",
            "DEBUG",
            action="retrieve",
            task=task_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "superuser_is_not_member_read_only",
        ],
    )
    def test_action_destroy_allowed(self, actor_fixture, task_read_only, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        req = build_request("delete", actor)
        result = TaskPermission().has_object_permission(req, DummyView("destroy"), task_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for action 'destroy': True",
            "DEBUG",
            action="destroy",
            task=task_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_action_destroy_not_allowed(
        self, actor_fixture, task_read_only, request, caplog_loguru
    ):
        actor, _ = request.getfixturevalue(actor_fixture)
        req = build_request("delete", actor)
        result = TaskPermission().has_object_permission(req, DummyView("destroy"), task_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for action 'destroy': False",
            "DEBUG",
            action="destroy",
            task=task_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "superuser_is_not_member_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_action_update_not_allowed(
        self, actor_fixture, task_read_only, request, caplog_loguru
    ):
        actor, _ = request.getfixturevalue(actor_fixture)
        req = build_request("put", actor)
        result = TaskPermission().has_object_permission(req, DummyView("update"), task_read_only)

        assert result is False

        log_record = caplog_loguru.records[-2]
        assert_log(
            log_record,
            "Permission Denied: Unrecognized action 'update'.",
            "WARNING",
            action="update",
            task=task_read_only.id,
        )

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
    def test_action_options_allowed(self, actor_fixture, task_read_only, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        req = build_request("options", actor)
        result = TaskPermission().has_object_permission(req, DummyView("options"), task_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for action 'options': False",
            "DEBUG",
            action="options",
            task=task_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "superuser_is_not_member_read_only",
        ],
    )
    def test_action_membership_allowed(
        self, actor_fixture, task_read_only, request, caplog_loguru
    ):
        actor, _ = request.getfixturevalue(actor_fixture)
        req = build_request("post", actor)
        result = TaskPermission().has_object_permission(
            req, DummyView("membership"), task_read_only
        )

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for action 'membership': True",
            "DEBUG",
            action="membership",
            task=task_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_action_membership_not_allowed(
        self, actor_fixture, task_read_only, request, caplog_loguru
    ):
        actor, _ = request.getfixturevalue(actor_fixture)
        req = build_request("post", actor)
        result = TaskPermission().has_object_permission(
            req, DummyView("membership"), task_read_only
        )

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for action 'membership': False",
            "DEBUG",
            action="membership",
            task=task_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "superuser_is_not_member_read_only",
        ],
    )
    def test_action_note_allowed(self, actor_fixture, task_read_only, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        req = build_request("post", actor)
        result = TaskPermission().has_object_permission(req, DummyView("note"), task_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for action 'note': True",
            "DEBUG",
            action="note",
            task=task_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_action_note_not_allowed(self, actor_fixture, task_read_only, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        req = build_request("post", actor)
        result = TaskPermission().has_object_permission(req, DummyView("note"), task_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for action 'note': False",
            "DEBUG",
            action="note",
            task=task_read_only.id,
        )
