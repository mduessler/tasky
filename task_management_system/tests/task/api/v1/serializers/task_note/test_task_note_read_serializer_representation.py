import pytest
from task.api.v1.serializers import TaskNoteReadSerializer
from tests.utils import build_request, to_iso


@pytest.mark.django_db
class TestRepresentation:
    def test_serializes_expected_fields(self, member_is_owner_read_only, task_note_read_only):
        actor, _ = member_is_owner_read_only

        task_note_read_only.note = "This is an important note"
        task_note_read_only.save()

        serializer = TaskNoteReadSerializer(
            instance=task_note_read_only,
            context={"request": build_request("get", actor)},
        )

        assert serializer.data["id"] == task_note_read_only.id
        assert serializer.data["note"] == "This is an important note"
        assert serializer.data["author"]["id"] == task_note_read_only.author.id
        assert serializer.data["task"] == task_note_read_only.task_id
        assert serializer.data["created_at"] == to_iso(task_note_read_only.created_at)
