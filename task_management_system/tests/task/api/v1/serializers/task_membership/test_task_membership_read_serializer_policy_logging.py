import pytest
from task.api.v1.serializers import TaskMembershipReadSerializer
from tests.utils import assert_log, build_request


@pytest.mark.django_db
class TestPolicyLogging:
    def test_can_delete_logging(self, task_membership, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner
        serializer = TaskMembershipReadSerializer(
            instance=task_membership,
            context={"request": build_request("get", actor)},
        )

        assert serializer.data["can_delete"] is True

        log_record = caplog_loguru.records[-6]
        assert_log(
            log_record,
            "User is allowed to delete task membership: ",
            "DEBUG",
            task=task_membership.task_id,
            membership=task_membership.id,
        )

    def test_editable_fields_logging(self, task_membership, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner
        serializer = TaskMembershipReadSerializer(
            instance=task_membership,
            context={"request": build_request("get", actor)},
        )

        assert "role" in serializer.data["editable_fields"]

        log_record = caplog_loguru.records[-5]
        assert_log(
            log_record,
            "User is allowed to update task membership: ",
            "DEBUG",
            task=task_membership.task_id,
            membership=task_membership.id,
        )
