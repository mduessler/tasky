from __future__ import annotations

from typing import Any

from django.utils.functional import cached_property
from rest_framework.serializers import ModelSerializer, SerializerMethodField


class BaseModelSerializer(ModelSerializer):  # type: ignore[misc]
    can_delete = SerializerMethodField()
    editable_fields = SerializerMethodField()

    class Meta:
        fields = [
            "can_delete",
            "editable_fields",
        ]
        read_only_fields = fields

    @cached_property  # type: ignore[misc]
    def request_user(self) -> Any:
        request = self.context.get("request")
        return getattr(request, "user", None)
