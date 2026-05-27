from loguru import logger
from task.models import TaskMembership
from task.policies import TaskMembershipPolicy
from user.api.v1.serializers import TmsUserReadSerializer

from task_management_system.core.api.v1.serializers import BaseModelSerializer
from task_management_system.core.logging.utils import bind_context_dict


class TaskMembershipReadSerializer(BaseModelSerializer):  # type: ignore[misc]
    user = TmsUserReadSerializer(read_only=True)

    class Meta(BaseModelSerializer.Meta):  # type: ignore[misc]
        model = TaskMembership
        fields = BaseModelSerializer.Meta.fields + [
            "id",
            "user",
            "task",
            "role",
            "joined_at",
        ]
        read_only_fields = fields

    def get_can_delete(self, membership: TaskMembership) -> bool:
        bind_context_dict(task=membership.task_id, membership=membership.id)
        result = TaskMembershipPolicy.can_delete(self.request_user, membership)
        logger.debug(f"User is allowed to delete task membership: {result}.")
        return result  # type: ignore[no-any-return]

    def get_editable_fields(self, membership: TaskMembership) -> list[str]:
        bind_context_dict(task=membership.task_id, membership=membership.id)
        result = TaskMembershipPolicy.get_editable_fields(self.request_user, membership)
        logger.debug(f"User is allowed to update task membership: {result}.")
        return list(result)
