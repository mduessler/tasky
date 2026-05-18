from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from loguru import logger
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, BaseThrottle
from rest_framework.viewsets import ModelViewSet
from task.api.v1.paginator import TaskMembershipPagination, TaskNotePagination, TaskPagination
from task.api.v1.serializers import (
    TaskMembershipReadSerializer,
    TaskNoteReadSerializer,
    TaskReadSerializer,
)
from user.api.v1.paginator import TmsUserPagination
from user.api.v1.serializers import TmsUserReadSerializer, TmsUserWriteSerializer
from user.api.v1.throttling import (
    TmsUserDeleteBurst,
    TmsUserDeleteSustained,
    TmsUserReadBurst,
    TmsUserReadSustained,
    TmsUserUpdateBurst,
    TmsUserUpdateSustained,
)
from user.models import TmsUser
from user.services import TmsUserService

from task_management_system.core.logging.utils import bind_context_dict


class TmsUserView(ModelViewSet):  # type: ignore[misc]
    http_method_names = ["delete", "get", "head", "options", "patch"]
    pagination_class = TmsUserPagination
    serializer_class = TmsUserReadSerializer
    queryset = TmsUser.objects.all()

    def get_throttles(self) -> list[BaseThrottle]:
        match self.action:
            case "retrieve" | "list":
                throttle_classes = [TmsUserReadBurst, TmsUserReadSustained]
            case "destroy":
                throttle_classes = [TmsUserDeleteBurst, TmsUserDeleteSustained]
            case "partial_update":
                throttle_classes = [TmsUserUpdateBurst, TmsUserUpdateSustained]
            case _:
                logger.warning(f"No throttle rate configured found for action '{self.action}'")
                throttle_classes = [AnonRateThrottle]
        return [throttle() for throttle in throttle_classes]

    def get_object(self) -> TmsUser:
        user_id = int(self.kwargs["pk"])
        return TmsUserService.get_user_via_id(self.request.user, user_id)

    def get_queryset(self) -> QuerySet[TmsUser]:
        return TmsUserService.get_users(self.request.user)

    @extend_schema(  # type: ignore[misc]
        request=TmsUserWriteSerializer,
        responses={200: TmsUserReadSerializer},
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        context = self.get_serializer_context()
        user = self.get_object()

        bind_context_dict(user=user.id)

        serializer = TmsUserWriteSerializer(user, data=request.data, partial=True, context=context)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()

        logger.debug("Successfully updated user.")

        read_serializer = TmsUserReadSerializer(updated_user, partial=True, context=context)
        return Response(read_serializer.data)

    def perform_destroy(self, instance: TmsUser) -> None:
        TmsUserService.delete(self.request.user, instance.id)

    def list_related_objects(self, queryset: QuerySet[Any]) -> Response:
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(  # type: ignore[misc]
        responses=TaskReadSerializer(many=True),
    )
    @action(detail=True, methods=["get"])  # type: ignore[misc]
    def tasks(self, request: Request, pk: int | None = None) -> Response:
        user = self.get_object()

        queryset = TmsUserService.get_tasks_of_user(self.request.user, user.id)

        self.pagination_class = TaskPagination
        self.serializer_class = TaskReadSerializer

        return self.list_related_objects(queryset)

    @extend_schema(  # type: ignore[misc]
        responses=TaskMembershipReadSerializer(many=True),
    )
    @action(detail=True, methods=["get"])  # type: ignore[misc]
    def task_memberships(self, request: Request, pk: int | None = None) -> Response:
        user = self.get_object()

        queryset = TmsUserService.get_memberships_of_user(self.request.user, user.id)

        self.pagination_class = TaskMembershipPagination
        self.serializer_class = TaskMembershipReadSerializer

        return self.list_related_objects(queryset)

    @extend_schema(  # type: ignore[misc]
        responses=TaskNoteReadSerializer(many=True),
    )
    @action(detail=True, methods=["get"])  # type: ignore[misc]
    def task_notes(self, request: Request, pk: int | None = None) -> Response:
        user = self.get_object()

        queryset = TmsUserService.get_notes_of_user(self.request.user, user.id)

        self.pagination_class = TaskNotePagination
        self.serializer_class = TaskNoteReadSerializer

        return self.list_related_objects(queryset)
