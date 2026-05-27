from typing import Any

from django.db.models.query import QuerySet
from drf_spectacular.utils import extend_schema
from loguru import logger
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.throttling import AnonRateThrottle, BaseThrottle
from rest_framework.viewsets import ModelViewSet
from task.api.v1.paginator import TaskMembershipPagination, TaskNotePagination, TaskPagination
from task.api.v1.permissions import TaskPermission
from task.api.v1.serializers import (
    TaskMembershipReadSerializer,
    TaskMembershipWriteSerializer,
    TaskNoteReadSerializer,
    TaskNoteWriteSerializer,
    TaskQuerySerializer,
    TaskReadSerializer,
    TaskWriteSerializer,
)
from task.api.v1.throttling import (
    TaskCreateBurst,
    TaskCreateSustained,
    TaskDeleteBurst,
    TaskDeleteSustained,
    TaskMembershipCreateBurst,
    TaskMembershipCreateSustained,
    TaskMembershipReadBurst,
    TaskMembershipReadSustained,
    TaskNoteCreateBurst,
    TaskNoteCreateSustained,
    TaskNoteReadBurst,
    TaskNoteReadSustained,
    TaskReadBurst,
    TaskReadSustained,
    TaskUpdateBurst,
    TaskUpdateSustained,
)
from task.models import Task
from task.services import TaskService

from task_management_system.core.logging.utils import bind_context_dict


class TaskViewSet(ModelViewSet):  # type: ignore[misc]
    serializer_class = TaskReadSerializer
    permission_classes = [IsAuthenticated, TaskPermission]
    http_method_names = ["delete", "get", "head", "options", "patch", "post"]
    pagination_class = TaskPagination
    queryset = Task.objects.all()

    def get_throttles(self) -> list[BaseThrottle]:
        match self.action:
            case "retrieve" | "list" | "metadata":
                throttle_classes = [TaskReadBurst, TaskReadSustained]
            case "destroy":
                throttle_classes = [TaskDeleteBurst, TaskDeleteSustained]
            case "partial_update":
                throttle_classes = [TaskUpdateBurst, TaskUpdateSustained]
            case "create":
                throttle_classes = [TaskCreateBurst, TaskCreateSustained]
            case "note":
                throttle_classes = [TaskNoteCreateBurst, TaskNoteCreateSustained]
            case "notes":
                throttle_classes = [TaskNoteReadBurst, TaskNoteReadSustained]
            case "membership":
                throttle_classes = [TaskMembershipCreateBurst, TaskMembershipCreateSustained]
            case "memberships":
                throttle_classes = [TaskMembershipReadBurst, TaskMembershipReadSustained]
            case _:
                logger.warning(f"No throttle rate configured found for action '{self.action}'")
                throttle_classes = [AnonRateThrottle]

        return [throttle() for throttle in throttle_classes]

    def get_object(self) -> Task:
        task_id = int(self.kwargs.get("pk"))
        return TaskService.get_task(self.request.user, task_id)

    def get_queryset(self) -> QuerySet[Task]:
        query_serializer = TaskQuerySerializer(
            data=self.request.query_params, context={"request": self.request}
        )
        query_serializer.is_valid(raise_exception=True)

        validated = query_serializer.validated_data
        status = validated.get("status")

        return TaskService.get_tasks(self.request.user, status)

    @extend_schema(  # type: ignore[misc]
        request=TaskWriteSerializer,
        responses={201: TaskReadSerializer},
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        context = self.get_serializer_context()

        write_serializer = TaskWriteSerializer(data=request.data, context=context)
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()

        logger.debug("Actor created a new task.")

        read_serializer = TaskReadSerializer(instance=instance, context=context)
        return Response(read_serializer.data, status=HTTP_201_CREATED)

    @extend_schema(  # type: ignore[misc]
        request=TaskWriteSerializer,
        responses={200: TaskReadSerializer},
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        task = self.get_object()
        context = self.get_serializer_context()

        bind_context_dict(task=task.id)

        write_serializer = TaskWriteSerializer(
            instance=task, data=request.data, partial=True, context=context
        )
        write_serializer.is_valid(raise_exception=True)
        updated_task = write_serializer.save()

        logger.debug("Successfully updated task object.")

        read_serializer = TaskReadSerializer(instance=updated_task, partial=True, context=context)
        return Response(read_serializer.data)

    def perform_destroy(self, task: Task) -> None:
        TaskService.delete(self.request.user, task.id)

    def list_related_objects(self, queryset: QuerySet[Any]) -> Response:
        logger.debug(f"Paginating queryset of size {queryset.count()} for action {self.action}.")

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create_related_object(
        self,
        request: Request,
        write_serializer_class: type[TaskMembershipWriteSerializer | TaskNoteWriteSerializer],
        read_serializer_class: type[TaskMembershipReadSerializer | TaskNoteReadSerializer],
    ) -> Response:
        task = self.get_object()
        bind_context_dict(task=task.id)

        logger.info("Actor attempts to create related object for task.")

        data = request.data.copy()
        data["task"] = task.id

        serializer = write_serializer_class(data=data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        logger.debug(f"Successfully created {instance.__class__.__name__}.")

        read_serializer = read_serializer_class(
            instance=instance, context=self.get_serializer_context()
        )

        return Response(read_serializer.data, status=HTTP_201_CREATED)

    @extend_schema(  # type: ignore[misc]
        responses=TaskMembershipReadSerializer(many=True),
    )
    @action(detail=True, methods=["get"])  # type: ignore[misc]
    def memberships(self, request: Request, pk: int | None = None) -> Response:
        task = self.get_object()

        queryset = TaskService.get_memberships_of_task(self.request.user, task)

        self.pagination_class = TaskMembershipPagination
        self.serializer_class = TaskMembershipReadSerializer

        return self.list_related_objects(queryset)

    @extend_schema(  # type: ignore[misc]
        request=TaskMembershipWriteSerializer,
        responses={201: TaskMembershipReadSerializer},
    )
    @action(detail=True, methods=["post"])  # type: ignore[misc]
    def membership(self, request: Request, pk: int | None = None) -> Response:
        return self.create_related_object(
            request=request,
            write_serializer_class=TaskMembershipWriteSerializer,
            read_serializer_class=TaskMembershipReadSerializer,
        )

    @extend_schema(  # type: ignore[misc]
        responses=TaskNoteReadSerializer(many=True),
    )
    @action(detail=True, methods=["get"])  # type: ignore[misc]
    def notes(self, request: Request, pk: int | None = None) -> Response:
        task = self.get_object()

        queryset = TaskService.get_notes_of_task(self.request.user, task)

        self.pagination_class = TaskNotePagination
        self.serializer_class = TaskNoteReadSerializer

        return self.list_related_objects(queryset)

    @extend_schema(  # type: ignore[misc]
        request=TaskNoteWriteSerializer,
        responses={201: TaskNoteReadSerializer},
    )
    @action(detail=True, methods=["post"])  # type: ignore[misc]
    def note(self, request: Request, pk: int | None = None) -> Response:
        return self.create_related_object(
            request=request,
            write_serializer_class=TaskNoteWriteSerializer,
            read_serializer_class=TaskNoteReadSerializer,
        )
