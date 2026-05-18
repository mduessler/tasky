from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from loguru import logger
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.viewsets import ModelViewSet
from task.api.v1.paginator import TaskMembershipPagination
from task.api.v1.permissions import TaskMembershipPermission
from task.api.v1.serializers import (
    TaskMembershipReadSerializer,
    TaskMembershipWriteSerializer,
)
from task.api.v1.throttling import (
    TaskMembershipDeleteBurst,
    TaskMembershipDeleteSustained,
    TaskMembershipReadBurst,
    TaskMembershipReadSustained,
    TaskMembershipUpdateBurst,
    TaskMembershipUpdateSustained,
)
from task.models import TaskMembership
from task.services import TaskMembershipService

from task_management_system.core.logging.utils import bind_context_dict


class TaskMembershipViewSet(ModelViewSet):  # type: ignore[misc]
    serializer_class = TaskMembershipReadSerializer
    permission_classes = [IsAuthenticated, TaskMembershipPermission]
    http_method_names = ["delete", "get", "head", "options", "patch"]
    pagination_class = TaskMembershipPagination
    queryset = TaskMembership.objects.all()

    def get_throttles(
        self,
    ) -> list[
        TaskMembershipDeleteBurst
        | TaskMembershipDeleteSustained
        | TaskMembershipReadBurst
        | TaskMembershipReadSustained
        | TaskMembershipUpdateBurst
        | TaskMembershipUpdateSustained
    ]:
        match self.action:
            case "retrieve" | "list" | "metadata":
                throttle_classes = [TaskMembershipReadBurst, TaskMembershipReadSustained]
            case "destroy":
                throttle_classes = [TaskMembershipDeleteBurst, TaskMembershipDeleteSustained]
            case "partial_update":
                throttle_classes = [TaskMembershipUpdateBurst, TaskMembershipUpdateSustained]
            case _:
                logger.critical(f"No throttle rate configured found for action '{self.action}'")
                throttle_classes = [AnonRateThrottle]

        return [throttle() for throttle in throttle_classes]

    def get_object(self) -> TaskMembership:
        membership_id = int(self.kwargs.get("pk"))
        return TaskMembershipService.get_task_membership(self.request.user, membership_id)

    def get_queryset(self) -> QuerySet[TaskMembership]:
        return TaskMembershipService.get_task_memberships(self.request.user)

    @extend_schema(  # type: ignore[misc]
        request=TaskMembershipWriteSerializer,
        responses={200: TaskMembershipReadSerializer},
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        membership = self.get_object()
        context = self.get_serializer_context()

        bind_context_dict(membership=membership.id)

        write_serializer = TaskMembershipWriteSerializer(
            instance=membership,
            data=request.data,
            partial=True,
            context=context,
        )
        write_serializer.is_valid(raise_exception=True)
        updated_membership = write_serializer.save()

        logger.debug("Successfully updated membership object.")

        read_serializer = TaskMembershipReadSerializer(
            instance=updated_membership, partial=True, context=context
        )
        return Response(read_serializer.data)

    def perform_destroy(self, membership: TaskMembership) -> None:
        TaskMembershipService.delete(self.request.user, membership.id)
