from typing import Any

from django.core.exceptions import PermissionDenied
from user.models import TmsUser
from user.services import TmsUserService

from task_management_system.core.api.v1.serializers import BaseModelSerializer


class TmsUserWriteSerializer(BaseModelSerializer):  # type: ignore[misc]
    class Meta(BaseModelSerializer.Meta):  # type: ignore[misc]
        model = TmsUser
        fields = [
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields: list[str] = []

    def create(self, _: dict[str, Any]) -> None:
        raise PermissionDenied("Not allowed to create a TmsUser with this serializer.")

    def update(self, instance: TmsUser, validated_data: dict[str, Any]) -> TmsUser:
        return TmsUserService.update(self.request_user, instance.id, validated_data)
