from typing import Any

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class JWTTokenObtainPairSerializer(TokenObtainPairSerializer):  # type: ignore[misc]
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(attrs)
        data["id"] = self.user.id

        return data  # type: ignore[no-any-return]
