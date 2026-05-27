from typing import Any

from drf_spectacular.utils import extend_schema
from loguru import logger
from registration.api.v1.permissions import RegisterUserPermission
from registration.api.v1.serializers import RegisterReadSerializer, RegisterWriteSerializer
from registration.api.v1.throttling import RegisterUserThrottle
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED


@extend_schema(
    request=RegisterWriteSerializer,
    responses={201: RegisterReadSerializer},
    tags=["auth"],
)
class RegisterUserView(CreateAPIView):  # type: ignore[misc]
    serializer_class = RegisterReadSerializer
    permission_classes = [AllowAny, RegisterUserPermission]
    throttle_classes = [RegisterUserThrottle]

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        context = self.get_serializer_context()

        write_serializer = RegisterWriteSerializer(data=request.data, context=context)
        write_serializer.is_valid(raise_exception=True)

        user = write_serializer.save()
        logger.debug("Sucessfully created a new user.")

        read_serializer = RegisterReadSerializer(user, context=context)
        return Response(read_serializer.data, status=HTTP_201_CREATED)
