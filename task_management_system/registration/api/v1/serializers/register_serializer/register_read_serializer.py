from rest_framework.serializers import ModelSerializer
from user.models import TmsUser


class RegisterReadSerializer(ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = TmsUser
        fields = ["email", "username"]
        read_only_fields = fields
