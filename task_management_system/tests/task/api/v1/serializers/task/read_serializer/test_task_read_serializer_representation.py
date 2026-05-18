import pytest
from task.api.v1.serializers import TaskReadSerializer
from task.policies import TaskPolicy
from tests.utils import build_request, to_iso


@pytest.mark.django_db
class TestRepresentation:
    def test_serializes_expected_fields(self, member_is_owner, task):
        actor, _ = member_is_owner
        serializer = TaskReadSerializer(
            instance=task, context={"request": build_request("get", actor)}
        )

        assert serializer.data["id"] == task.id
        assert serializer.data["title"] == task.title
        assert serializer.data["description"] == task.description
        assert serializer.data["status"] == task.status
        assert serializer.data["created_at"] == to_iso(task.created_at)

        assert serializer.data["can_delete"] == TaskPolicy.can_delete(actor, task)
        assert serializer.data["editable_fields"] == list(
            TaskPolicy.get_editable_fields(actor, task)
        )
