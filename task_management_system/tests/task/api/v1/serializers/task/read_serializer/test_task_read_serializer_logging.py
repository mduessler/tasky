import pytest
from task.api.v1.serializers import TaskReadSerializer
from tests.utils import assert_log, build_request


@pytest.mark.django_db
class TestPolicyLogging:
    def test_get_can_delete_logging(self, task, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner
        serializer = TaskReadSerializer(
            instance=task, context={"request": build_request("get", actor)}
        )

        assert serializer.data["can_delete"] is True

        log_record = caplog_loguru.records[-2]
        assert_log(
            log_record,
            "User is allowed to delete task: True.",
            "DEBUG",
            task=task.id,
        )

    def test_get_editable_fields_logging(self, task, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner
        serializer = TaskReadSerializer(
            instance=task, context={"request": build_request("get", actor)}
        )

        assert "title" in serializer.data["editable_fields"]

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "User is allowed to update task: ",
            "DEBUG",
            task=task.id,
        )
