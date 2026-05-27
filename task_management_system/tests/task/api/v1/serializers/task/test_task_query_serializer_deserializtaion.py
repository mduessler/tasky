import pytest
from task.api.v1.serializers import TaskQuerySerializer
from tests.utils import (
    build_request,
)


@pytest.mark.django_db
class TestTaskQuerySerializerDeserialization:
    def test_task_query_serializer_valid(self, member_is_owner):
        actor, _ = member_is_owner
        data = {"status": "todo"}
        serializer = TaskQuerySerializer(
            data=data, context={"request": build_request("get", actor)}
        )

        assert serializer.is_valid() is True
        assert serializer.validated_data["status"] == "todo"

    def test_task_query_serializer_invalid(self, superuser):
        data = {"status": "invalid"}
        serializer = TaskQuerySerializer(
            data=data, context={"request": build_request("get", superuser)}
        )

        assert serializer.is_valid() is False

    def test_task_query_serializer_empty(self, superuser):
        serializer = TaskQuerySerializer(
            data={}, context={"request": build_request("get", superuser)}
        )

        assert serializer.is_valid() is True
        assert serializer.validated_data == {}
