from unittest.mock import MagicMock

import pytest
from task.api.v1.serializers import TaskWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestServiceHandoff:
    def test_create_handoff_to_service(self, active_user, monkeypatch):
        data = {
            "title": "New Task",
            "description": "Description",
            "status": "todo",
        }

        mock_create = MagicMock(return_value=MagicMock())
        monkeypatch.setattr("task.services.TaskService.create", mock_create)

        serializer = TaskWriteSerializer(
            data=data, context={"request": build_request("post", active_user)}
        )

        assert serializer.is_valid() is True
        serializer.save()

        mock_create.assert_called_once_with(active_user, serializer.validated_data)

    def test_update_handoff_to_service(self, active_user, monkeypatch):
        task = MagicMock(id=1)
        data = {"title": "Updated Title"}

        mock_update = MagicMock(return_value=task)
        monkeypatch.setattr("task.services.TaskService.update", mock_update)

        serializer = TaskWriteSerializer(
            instance=task,
            data=data,
            partial=True,
            context={"request": build_request("patch", active_user)},
        )

        assert serializer.is_valid() is True
        serializer.save()

        mock_update.assert_called_once_with(active_user, task.id, serializer.validated_data)
