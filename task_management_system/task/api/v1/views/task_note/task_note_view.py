from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from loguru import logger
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.viewsets import ModelViewSet
from task.api.v1.paginator import TaskNotePagination
from task.api.v1.permissions import TaskNotePermission
from task.api.v1.serializers import TaskNoteReadSerializer, TaskNoteWriteSerializer
from task.api.v1.throttling import (
    TaskNoteDeleteBurst,
    TaskNoteDeleteSustained,
    TaskNoteReadBurst,
    TaskNoteReadSustained,
    TaskNoteUpdateBurst,
    TaskNoteUpdateSustained,
)
from task.models import TaskNote
from task.services import TaskNoteService

from task_management_system.core.logging.utils import bind_context_dict


class TaskNoteViewSet(ModelViewSet):  # type: ignore[misc]
    serializer_class = TaskNoteReadSerializer
    permission_classes = [IsAuthenticated, TaskNotePermission]
    http_method_names = ["delete", "get", "head", "options", "patch"]
    pagination_class = TaskNotePagination
    queryset = TaskNote.objects.all()

    def get_throttles(
        self,
    ) -> list[
        TaskNoteDeleteBurst
        | TaskNoteDeleteSustained
        | TaskNoteReadBurst
        | TaskNoteReadSustained
        | TaskNoteUpdateBurst
        | TaskNoteUpdateSustained
    ]:
        match self.action:
            case "retrieve" | "list" | "metadata":
                self.throttle_classes = [TaskNoteReadBurst, TaskNoteReadSustained]
            case "destroy":
                self.throttle_classes = [TaskNoteDeleteBurst, TaskNoteDeleteSustained]
            case "partial_update":
                self.throttle_classes = [TaskNoteUpdateBurst, TaskNoteUpdateSustained]
            case _:
                logger.critical(f"No throttle rate configured found for action '{self.action}'")
                self.throttle_classes = [AnonRateThrottle]

        return [throttle() for throttle in self.throttle_classes]

    def get_object(self) -> TaskNote:
        note_id = int(self.kwargs.get("pk"))
        return TaskNoteService.get_task_note(self.request.user, note_id)

    def get_queryset(self) -> QuerySet[TaskNote]:
        return TaskNoteService.get_task_notes(self.request.user)

    @extend_schema(  # type: ignore[misc]
        request=TaskNoteWriteSerializer,
        responses={200: TaskNoteReadSerializer},
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        note = self.get_object()
        context = self.get_serializer_context()

        bind_context_dict(note=note.id)

        write_serializer = TaskNoteWriteSerializer(
            instance=note,
            data=request.data,
            partial=True,
            context=context,
        )
        write_serializer.is_valid(raise_exception=True)
        updated_note = write_serializer.save()

        logger.debug("Successfully updated note object.")

        read_serializer = TaskNoteReadSerializer(
            instance=updated_note,
            partial=True,
            context=context,
        )
        return Response(read_serializer.data)

    def perform_destroy(self, note: TaskNote) -> None:
        TaskNoteService.delete(self.request.user, note.id)
