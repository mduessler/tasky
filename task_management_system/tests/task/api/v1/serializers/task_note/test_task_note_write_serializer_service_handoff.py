from unittest.mock import MagicMock

import pytest
from task.api.v1.serializers import TaskNoteWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestServiceHandoff:
    def test_create_handoff_to_service(self, member_is_owner, task, monkeypatch):
        actor, _ = member_is_owner
        data = {"note": "This is an important note", "author_id": actor.id, "task": task.id}

        mock_create = MagicMock(return_value=MagicMock())
        monkeypatch.setattr("task.services.TaskNoteService.create", mock_create)

        serializer = TaskNoteWriteSerializer(
            data=data, context={"request": build_request("post", actor)}
        )
        assert serializer.is_valid() is True
        serializer.save()

        mock_create.assert_called_once_with(actor, serializer.validated_data)

    def test_update_handoff_to_service(self, member_is_owner, task_note, monkeypatch):
        actor, _ = member_is_owner
        data = {"note": "This is an important note"}

        mock_update = MagicMock(return_value=task_note)
        monkeypatch.setattr("task.services.TaskNoteService.update", mock_update)

        serializer = TaskNoteWriteSerializer(
            instance=task_note,
            data=data,
            partial=True,
            context={"request": build_request("patch", actor)},
        )
        assert serializer.is_valid() is True
        serializer.save()

        mock_update.assert_called_once_with(actor, task_note.id, serializer.validated_data)
