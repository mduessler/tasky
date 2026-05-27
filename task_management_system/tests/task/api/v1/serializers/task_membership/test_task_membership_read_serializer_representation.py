import pytest
from task.api.v1.serializers import TaskMembershipReadSerializer
from task.policies import TaskMembershipPolicy
from tests.utils import build_request, to_iso


@pytest.mark.django_db
class TestRepresentation:
    def test_serializes_expected_fields(
        self, member_is_owner_read_only, task_membership_read_only
    ):
        actor, _ = member_is_owner_read_only
        serializer = TaskMembershipReadSerializer(
            instance=task_membership_read_only,
            context={"request": build_request("get", actor)},
        )

        assert serializer.data["id"] == task_membership_read_only.id
        assert serializer.data["role"] == task_membership_read_only.role
        assert serializer.data["task"] == task_membership_read_only.task_id
        assert serializer.data["joined_at"] == to_iso(task_membership_read_only.joined_at)

        assert serializer.data["user"]["id"] == task_membership_read_only.user.id
        assert serializer.data["user"]["email"] == task_membership_read_only.user.email

        assert serializer.data["can_delete"] == TaskMembershipPolicy.can_delete(
            actor,
            task_membership_read_only,
        )

        assert serializer.data["editable_fields"] == list(
            TaskMembershipPolicy.get_editable_fields(actor, task_membership_read_only)
        )
