import pytest
from task.api.v1.serializers import TaskReadSerializer
from task.policies import TaskPolicy
from tests.utils import build_request, to_iso


@pytest.mark.django_db
class TestRepresentation:
    def test_serializes_expected_fields(self, member_is_owner_read_only, task_read_only):
        actor, _ = member_is_owner_read_only
        serializer = TaskReadSerializer(
            instance=task_read_only, context={"request": build_request("get", actor)}
        )

        assert serializer.data["id"] == task_read_only.id
        assert serializer.data["title"] == task_read_only.title
        assert serializer.data["description"] == task_read_only.description
        assert serializer.data["status"] == task_read_only.status
        assert serializer.data["created_at"] == to_iso(task_read_only.created_at)

        assert serializer.data["can_delete"] == TaskPolicy.can_delete(actor, task_read_only)
        assert serializer.data["editable_fields"] == list(
            TaskPolicy.get_editable_fields(actor, task_read_only)
        )
