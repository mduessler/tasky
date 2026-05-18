import pytest
from task.api.v1.serializers import TaskWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestValidation:
    def test_title_too_long(self, active_user, data_task):
        data_task["title"] = "   "
        serializer = TaskWriteSerializer(
            data=data_task, context={"request": build_request("post", active_user)}
        )

        assert serializer.is_valid() is False
        assert "title" in serializer.errors

    def test_invalid_status(self, active_user, data_task):
        data_task["status"] = "invalid"

        serializer = TaskWriteSerializer(
            data=data_task, context={"request": build_request("post", active_user)}
        )

        assert serializer.is_valid() is False
        assert "status" in serializer.errors
