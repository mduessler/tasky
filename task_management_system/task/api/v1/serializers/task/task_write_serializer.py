from __future__ import annotations

from typing import Any

from task.models import Task
from task.services import TaskService

from task_management_system.core.api.v1.serializers import BaseModelSerializer


class TaskWriteSerializer(BaseModelSerializer):  # type: ignore[misc]
    class Meta(BaseModelSerializer.Meta):  # type: ignore[misc]
        model = Task
        fields = [
            "title",
            "description",
            "status",
        ]
        read_only_fields: list[str] = []

    def create(self, validated_data: dict[str, Any]) -> Task:
        return TaskService.create(self.request_user, validated_data)

    def update(self, instance: Task, validated_data: dict[str, Any]) -> Task:
        return TaskService.update(self.request_user, instance.id, validated_data)
