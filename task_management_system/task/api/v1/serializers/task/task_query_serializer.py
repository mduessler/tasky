from functools import cached_property
from typing import Any

from rest_framework.serializers import ChoiceField, Serializer
from task.models import TaskStatus


class TaskQuerySerializer(Serializer):  # type: ignore[misc]
    status = ChoiceField(choices=TaskStatus.choices, required=False)

    @cached_property
    def request_user(self) -> Any:
        request = self.context.get("request")
        return getattr(request, "user", None)
