from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from tms_auth.api.v1.serializers import JWTRefreshSerializer
from tms_auth.api.v1.throttling import RefreshJwtThrottleBurst, RefreshJwtThrottleSustained


@extend_schema(tags=["auth"])
class JwtRefreshView(TokenRefreshView):  # type: ignore[misc]
    serializer_class = JWTRefreshSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RefreshJwtThrottleBurst, RefreshJwtThrottleSustained]
