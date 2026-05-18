from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework.permissions import AllowAny
from rest_framework.serializers import CharField, IntegerField
from rest_framework_simplejwt.views import TokenObtainPairView
from tms_auth.api.v1.serializers import JWTTokenObtainPairSerializer
from tms_auth.api.v1.throttling import LoginJwtThrottleBurst, LoginJwtThrottleSustained


@extend_schema(
    tags=["auth"],
    responses={
        200: inline_serializer(
            name="JWTTokenObtainPairResponse",
            fields={
                "id": IntegerField(),
                "access": CharField(),
                "refresh": CharField(),
            },
        )
    },
)
class JwtTokenObtainPairView(TokenObtainPairView):  # type: ignore[misc]
    serializer_class = JWTTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginJwtThrottleBurst, LoginJwtThrottleSustained]
