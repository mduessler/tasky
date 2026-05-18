from rest_framework.serializers import CharField
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer


class JWTLogoutSerializer(TokenBlacklistSerializer):  # type: ignore[misc]
    refresh = CharField()
