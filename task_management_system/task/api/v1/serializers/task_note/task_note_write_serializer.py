from __future__ import annotations

from typing import Any

from rest_framework.serializers import PrimaryKeyRelatedField
from task.models import TaskNote
from task.services import TaskNoteService
from user.models import TmsUser

from task_management_system.core.api.v1.serializers import BaseModelSerializer


class TaskNoteWriteSerializer(BaseModelSerializer):  # type: ignore[misc]
    author_id = PrimaryKeyRelatedField(
        queryset=TmsUser.objects.all(),
        source="author",
    )

    class Meta:
        model = TaskNote
        fields = ["note", "author_id", "task"]
        read_only_fields: list[str] = []

    def create(self, validated_data: dict[str, Any]) -> TaskNote:
        validated_data["author"] = self.request_user
        return TaskNoteService.create(self.request_user, validated_data)

    def update(self, instance: TaskNote, validated_data: dict[str, Any]) -> TaskNote:
        validated_data.pop("task", None)
        validated_data.pop("author", None)
        return TaskNoteService.update(self.request_user, instance.id, validated_data)
