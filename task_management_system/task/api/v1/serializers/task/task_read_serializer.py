from __future__ import annotations

from loguru import logger
from task.models import Task
from task.policies import TaskPolicy

from task_management_system.core.api.v1.serializers import BaseModelSerializer
from task_management_system.core.logging.utils import bind_context_dict


class TaskReadSerializer(BaseModelSerializer):  # type: ignore[misc]
    class Meta(BaseModelSerializer.Meta):  # type: ignore[misc]
        model = Task
        fields = BaseModelSerializer.Meta.fields + [
            "id",
            "title",
            "description",
            "status",
            "created_at",
        ]
        read_only_fields = fields

    def get_can_delete(self, task: Task) -> bool:
        bind_context_dict(task=task.id)
        result = TaskPolicy.can_delete(self.request_user, task)
        logger.debug(f"User is allowed to delete task: {result}.")
        return result  # type: ignore[no-any-return]

    def get_editable_fields(self, task: Task) -> list[str]:
        bind_context_dict(task=task.id)
        result = TaskPolicy.get_editable_fields(self.request_user, task)
        logger.debug(f"User is allowed to update task: {result}.")
        return list(result)
