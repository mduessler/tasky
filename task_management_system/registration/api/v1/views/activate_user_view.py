from typing import Any

from drf_spectacular.utils import extend_schema
from loguru import logger
from registration.api.v1.permissions import ActivateUserPermission
from registration.api.v1.serializers import ActivateReadSerializer, ActivateWriteSerializer
from registration.api.v1.throttling import ActivateUserThrottle
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_202_ACCEPTED
from rest_framework.views import APIView, Request, Response


class ActivateUserView(APIView):  # type: ignore[misc]
    serializer_class = ActivateReadSerializer
    permission_classes = [AllowAny, ActivateUserPermission]
    throttle_classes = [ActivateUserThrottle]

    http_method_names = ["options", "post"]

    @extend_schema(  # type: ignore[misc]
        request=ActivateWriteSerializer,
        responses={202: ActivateReadSerializer},
        tags=["auth"],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        context = {"request": self.request}

        write_serializer = ActivateWriteSerializer(data=request.data, context=context)
        write_serializer.is_valid(raise_exception=True)

        user = write_serializer.save()
        logger.debug("Sucessfully activated user.")

        read_serializer = ActivateReadSerializer(user, context=context)
        return Response(read_serializer.data, status=HTTP_202_ACCEPTED)
