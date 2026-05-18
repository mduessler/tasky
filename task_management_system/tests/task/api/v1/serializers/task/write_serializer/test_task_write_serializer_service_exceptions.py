import pytest
from rest_framework.exceptions import ValidationError
from task.api.v1.serializers import TaskWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestServiceExceptions:
    def test_create_service_raises_error(self, active_user, monkeypatch, data_task):
        def mock_create(self, *args, **kwargs):
            raise ValidationError({"detail": "Limit reached"})

        monkeypatch.setattr("task.services.TaskService.create", mock_create)

        serializer = TaskWriteSerializer(
            data=data_task, context={"request": build_request("post", active_user)}
        )

        assert serializer.is_valid() is True
        with pytest.raises(ValidationError) as exc:
            serializer.save()

        assert exc.value.detail["detail"] == "Limit reached"
