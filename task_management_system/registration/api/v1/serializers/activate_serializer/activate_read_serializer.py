from rest_framework.serializers import ModelSerializer
from user.models import TmsUser


class ActivateReadSerializer(ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = TmsUser
        fields = ["id", "email", "username"]
        read_only_fields = fields
