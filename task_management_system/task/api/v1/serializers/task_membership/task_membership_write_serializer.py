from typing import Any

from rest_framework.serializers import PrimaryKeyRelatedField
from task.models import TaskMembership
from task.services import TaskMembershipService
from user.models import TmsUser

from task_management_system.core.api.v1.serializers import BaseModelSerializer


class TaskMembershipWriteSerializer(BaseModelSerializer):  # type: ignore[misc]
    user_id = PrimaryKeyRelatedField(
        queryset=TmsUser.objects.all(),
        source="user",
    )

    class Meta:
        model = TaskMembership
        fields = ["role", "user_id", "task"]
        read_only_fields: list[str] = []

    def create(self, validated_data: dict[str, Any]) -> TaskMembership:
        return TaskMembershipService.create(self.request_user, validated_data)

    def update(self, instance: TaskMembership, validated_data: dict[str, Any]) -> TaskMembership:
        validated_data.pop("task", None)
        validated_data.pop("user", None)
        return TaskMembershipService.update(self.request_user, instance.id, validated_data)
