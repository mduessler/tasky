import pytest
from task.api.v1.serializers import TaskNoteReadSerializer
from tests.utils import assert_log, build_request


@pytest.mark.django_db
class TestPolicyLogging:
    def test_can_delete_logging(self, task_note, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner

        serializer = TaskNoteReadSerializer(
            instance=task_note,
            context={"request": build_request("get", actor)},
        )

        assert serializer.data["can_delete"] is True

        log_record = caplog_loguru.records[-4]

        assert_log(
            log_record,
            "Permission granted: User can delete itself.",
            "DEBUG",
            task=task_note.task_id,
            note=task_note.id,
        )

    def test_editable_fields_logging(self, task_note, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner

        serializer = TaskNoteReadSerializer(
            instance=task_note,
            context={"request": build_request("get", actor)},
        )

        assert "note" in serializer.data["editable_fields"]

        log_record = caplog_loguru.records[-5]

        assert_log(
            log_record,
            "User is allowed to update task note: {'note'}.",
            "DEBUG",
            task=task_note.task_id,
            note=task_note.id,
        )
