from loguru import logger
from user.models import TmsUser
from user.policies import TmsUserPolicy

from task_management_system.core.api.v1.serializers import BaseModelSerializer
from task_management_system.core.logging.utils import bind_context_dict


class TmsUserReadSerializer(BaseModelSerializer):  # type: ignore[misc]
    class Meta(BaseModelSerializer.Meta):  # type: ignore[misc]
        model = TmsUser
        fields = BaseModelSerializer.Meta.fields + [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
        ]
        read_only_fields = fields

    def get_can_delete(self, user: TmsUser) -> bool:
        bind_context_dict(user=user.id)
        result = TmsUserPolicy.can_delete(self.request_user, user)
        logger.debug(f"Actor is allowed to delete user: {result}.")
        return result  # type: ignore[no-any-return]

    def get_editable_fields(self, user: TmsUser) -> list[str]:
        bind_context_dict(user=user.id)
        result = TmsUserPolicy.get_editable_fields(self.request_user, user)
        logger.debug(f"Actor is allowed to update user: {result}.")
        return list(result)
