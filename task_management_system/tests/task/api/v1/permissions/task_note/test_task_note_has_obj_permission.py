import pytest
from task.api.v1.permissions import TaskNotePermission
from tests.utils import DummyView, assert_log, build_request


@pytest.mark.django_db
class TestHasObjPermission:
    def test_view_has_no_action(
        self, member_is_owner_read_only, task_note_read_only, caplog_loguru
    ):
        actor, _ = member_is_owner_read_only
        req = build_request("get", actor)
        result = TaskNotePermission().has_object_permission(req, object(), task_note_read_only)

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
    def test_action_create_is_not_allowed(
        self, actor_data, task_note_read_only, request, caplog_loguru
    ):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("post", actor)
        result = TaskNotePermission().has_object_permission(
            req, DummyView("create"), task_note_read_only
        )

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for task note action 'create': False",
            "DEBUG",
            action="create",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
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
    def test_action_retrieve_allowed(
        self, actor_data, task_note_read_only, request, caplog_loguru
    ):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("get", actor)
        result = TaskNotePermission().has_object_permission(
            req, DummyView("retrieve"), task_note_read_only
        )

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for task note action 'retrieve': True",
            "DEBUG",
            action="retrieve",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
        )

    def test_action_retrieve_not_allowed(
        self, user_is_not_member_read_only, task_note_read_only, request, caplog_loguru
    ):
        actor, _ = user_is_not_member_read_only
        req = build_request("get", actor)
        result = TaskNotePermission().has_object_permission(
            req, DummyView("retrieve"), task_note_read_only
        )

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for task note action 'retrieve': False",
            "DEBUG",
            action="retrieve",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "superuser_is_not_member_read_only",
        ],
    )
    def test_action_destroy_allowed(self, actor_data, task_note_read_only, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("delete", actor)
        result = TaskNotePermission().has_object_permission(
            req, DummyView("destroy"), task_note_read_only
        )

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for task note action 'destroy': True",
            "DEBUG",
            action="destroy",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_action_destroy_not_allowed(
        self, actor_data, task_note_read_only, request, caplog_loguru
    ):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("delete", actor)
        result = TaskNotePermission().has_object_permission(
            req, DummyView("destroy"), task_note_read_only
        )

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for task note action 'destroy': False",
            "DEBUG",
            action="destroy",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "superuser_is_not_member_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_action_update_allowed(self, actor_data, task_note_read_only, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("put", actor)
        result = TaskNotePermission().has_object_permission(
            req, DummyView("update"), task_note_read_only
        )

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for task note action 'update': False",
            "DEBUG",
            action="update",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
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
    def test_action_options_allowed(self, actor_data, task_note_read_only, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_data)
        req = build_request("options", actor)
        result = TaskNotePermission().has_object_permission(
            req, DummyView("options"), task_note_read_only
        )

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Has object permission for task note action 'options': False",
            "DEBUG",
            action="options",
            task=task_note_read_only.task.id,
            note=task_note_read_only.id,
        )
