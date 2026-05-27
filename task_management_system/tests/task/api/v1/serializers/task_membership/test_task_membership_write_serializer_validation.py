import pytest
from task.api.v1.serializers import TaskMembershipWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestValidation:
    def test_required_fields(self, active_user):
        serializer = TaskMembershipWriteSerializer(
            data={},
            context={"request": build_request("post", active_user)},
        )

        assert serializer.is_valid() is False
        assert "role" in serializer.errors
        assert "user_id" in serializer.errors
        assert "task" in serializer.errors
