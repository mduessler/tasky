import pytest
from task.api.v1.serializers import TaskNoteWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestValidation:
    def test_note_is_required(self, member_is_owner):
        actor, _ = member_is_owner

        serializer = TaskNoteWriteSerializer(
            data={},
            context={"request": build_request("post", actor)},
        )

        assert serializer.is_valid() is False
        assert "note" in serializer.errors

    def test_author_id_is_required(self, member_is_owner):
        actor, _ = member_is_owner

        serializer = TaskNoteWriteSerializer(
            data={"note": "This is an important note"},
            context={"request": build_request("post", actor)},
        )

        assert serializer.is_valid() is False
        assert "task" in serializer.errors
        assert "author_id" in serializer.errors
