import pytest
from task.api.v1.serializers import TaskNoteReadSerializer
from tests.utils import build_request, to_iso


@pytest.mark.django_db
class TestRepresentation:
    def test_serializes_expected_fields(self, member_is_owner, task_note):
        actor, _ = member_is_owner

        task_note.note = "This is an important note"
        task_note.save()

        serializer = TaskNoteReadSerializer(
            instance=task_note,
            context={"request": build_request("get", actor)},
        )

        assert serializer.data["id"] == task_note.id
        assert serializer.data["note"] == "This is an important note"
        assert serializer.data["author"]["id"] == task_note.author.id
        assert serializer.data["task"] == task_note.task_id
        assert serializer.data["created_at"] == to_iso(task_note.created_at)
