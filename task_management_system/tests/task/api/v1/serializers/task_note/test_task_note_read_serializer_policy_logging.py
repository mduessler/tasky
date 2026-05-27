import pytest
from task.api.v1.serializers import TaskNoteReadSerializer
from tests.utils import assert_log, build_request


@pytest.mark.django_db
class TestPolicyLogging:
    def test_can_delete_logging(
        self, task_note_read_only, member_is_owner_read_only, caplog_loguru
    ):
        actor, _ = member_is_owner_read_only

        serializer = TaskNoteReadSerializer(
            instance=task_note_read_only,
            context={"request": build_request("get", actor)},
        )

        assert serializer.data["can_delete"] is True

        log_record = caplog_loguru.records[-4]

        assert_log(
            log_record,
            "Permission granted: User can delete itself.",
            "DEBUG",
            task=task_note_read_only.task_id,
            note=task_note_read_only.id,
        )

    def test_editable_fields_logging(
        self, task_note_read_only, member_is_owner_read_only, caplog_loguru
    ):
        actor, _ = member_is_owner_read_only

        serializer = TaskNoteReadSerializer(
            instance=task_note_read_only,
            context={"request": build_request("get", actor)},
        )

        assert "note" in serializer.data["editable_fields"]

        log_record = caplog_loguru.records[-5]

        assert_log(
            log_record,
            "User is allowed to update task note: {'note'}.",
            "DEBUG",
            task=task_note_read_only.task_id,
            note=task_note_read_only.id,
        )
