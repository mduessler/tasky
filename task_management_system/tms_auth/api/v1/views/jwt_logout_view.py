from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenBlacklistView
from tms_auth.api.v1.serializers import JWTLogoutSerializer
from tms_auth.api.v1.throttling import (
    LogoutJwtThrottleBurst,
    LogoutJwtThrottleSustained,
)


@extend_schema(tags=["auth"])
class JwtLogoutView(TokenBlacklistView):  # type: ignore[misc]
    serializer_class = JWTLogoutSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    throttle_classes = [
        LogoutJwtThrottleBurst,
        LogoutJwtThrottleSustained,
    ]
