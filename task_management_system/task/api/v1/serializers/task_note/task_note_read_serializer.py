from __future__ import annotations

from loguru import logger
from task.models import TaskNote
from task.policies import TaskNotePolicy
from user.api.v1.serializers import TmsUserReadSerializer

from task_management_system.core.api.v1.serializers import BaseModelSerializer
from task_management_system.core.logging.utils import bind_context_dict


class TaskNoteReadSerializer(BaseModelSerializer):  # type: ignore[misc]
    author = TmsUserReadSerializer(read_only=True)

    class Meta(BaseModelSerializer.Meta):  # type: ignore[misc]
        model = TaskNote
        fields = BaseModelSerializer.Meta.fields + [
            "id",
            "note",
            "author",
            "task",
            "created_at",
        ]
        read_only_fields = fields

    def get_can_delete(self, note: TaskNote) -> bool:
        bind_context_dict(task=note.task_id, note=note.id)
        result = TaskNotePolicy.can_delete(self.request_user, note)
        logger.debug(f"User is allowed to delete task note: {result}.")
        return result  # type: ignore[no-any-return]

    def get_editable_fields(self, note: TaskNote) -> list[str]:
        bind_context_dict(task=note.task_id, note=note.id)
        result = TaskNotePolicy.get_editable_fields(self.request_user, note)
        logger.debug(f"User is allowed to update task note: {result}.")
        return list(result)
