from rest_framework.serializers import ModelSerializer
from user.models import TmsUser


class TmsUserSerializer(ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = TmsUser
        fields = ["id", "email", "username"]


class UserSummarySerializer(ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = TmsUser
        fields = ["id", "email", "username"]
