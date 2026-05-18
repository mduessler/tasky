import pytest
from task.api.v1.serializers import TaskMembershipReadSerializer
from task.policies import TaskMembershipPolicy
from tests.utils import build_request, to_iso


@pytest.mark.django_db
class TestRepresentation:
    def test_serializes_expected_fields(self, member_is_owner, task_membership):
        actor, _ = member_is_owner
        serializer = TaskMembershipReadSerializer(
            instance=task_membership,
            context={"request": build_request("get", actor)},
        )

        assert serializer.data["id"] == task_membership.id
        assert serializer.data["role"] == task_membership.role
        assert serializer.data["task"] == task_membership.task_id
        assert serializer.data["joined_at"] == to_iso(task_membership.joined_at)

        assert serializer.data["user"]["id"] == task_membership.user.id
        assert serializer.data["user"]["email"] == task_membership.user.email

        assert serializer.data["can_delete"] == TaskMembershipPolicy.can_delete(
            actor,
            task_membership,
        )

        assert serializer.data["editable_fields"] == list(
            TaskMembershipPolicy.get_editable_fields(actor, task_membership)
        )
