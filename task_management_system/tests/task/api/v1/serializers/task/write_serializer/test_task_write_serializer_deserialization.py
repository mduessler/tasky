import pytest
from task.api.v1.serializers import TaskWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestDeserialization:
    def test_validates_input_correctly(self, member_is_owner, data_task):
        actor, _ = member_is_owner

        serializer = TaskWriteSerializer(
            data=data_task,
            context={"request": build_request("post", actor)},
        )

        assert serializer.is_valid() is True
        assert serializer.validated_data["title"] == data_task["title"]
        assert serializer.validated_data["description"] == data_task["description"]
        assert serializer.validated_data["status"] == data_task["status"]

        assert "created_at" not in serializer.validated_data
