from typing import Any

from registration.services import RegistrationService
from rest_framework.serializers import CharField, EmailField, Serializer
from user.models import TmsUser


class ActivateWriteSerializer(Serializer):  # type: ignore[misc]
    email = EmailField(write_only=True)
    token = CharField(write_only=True)

    def save(self, **kwargs: Any) -> TmsUser:
        return RegistrationService.activate_user(**self.validated_data)
