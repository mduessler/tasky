import pytest
from django.core.exceptions import ValidationError
from task.models import Role, TaskMembership, TaskNote


@pytest.mark.django_db
class TestTaskNote:

    def test_create_note_success(self, task_read_only, active_user_read_only):
        TaskMembership.objects.create(
            user=active_user_read_only, task=task_read_only, role=Role.MEMBER
        )

        note_text = "This is an important note"
        note = TaskNote.objects.create(
            task=task_read_only, author=active_user_read_only, note=note_text
        )

        assert note.pk is not None
        assert note.note == note_text
        assert note.author == active_user_read_only

    def test_create_note_author_not_member_raises_error(
        self, task_read_only, active_user_read_only
    ):
        with pytest.raises(ValidationError) as excinfo:
            TaskNote.objects.create(
                task=task_read_only, author=active_user_read_only, note="This is an important note"
            )
        assert "Author must be a member of the task." in str(excinfo.value)

    def test_create_note_without_author_success(self, task_read_only):
        note = TaskNote.objects.create(
            task=task_read_only, author=None, note="This is an important note"
        )
        assert note.author is None
        assert note.pk is not None

    def test_note_content_cannot_be_empty(self, task_read_only, active_user_read_only):
        TaskMembership.objects.create(
            user=active_user_read_only, task=task_read_only, role=Role.MEMBER
        )

        with pytest.raises(ValidationError):
            TaskNote.objects.create(task=task_read_only, author=active_user_read_only, note="")

    def test_on_delete_set_null_author(self, task_read_only, active_user_read_only):
        TaskMembership.objects.create(
            user=active_user_read_only, task=task_read_only, role=Role.MEMBER
        )
        note = TaskNote.objects.create(
            task=task_read_only, author=active_user_read_only, note="This is an important note"
        )

        active_user_read_only.delete()
        note.refresh_from_db()

        assert note.author is None
        assert note.note == "This is an important note"

    def test_on_delete_cascade_task(self, task_read_only, active_user_read_only):
        TaskMembership.objects.create(
            user=active_user_read_only, task=task_read_only, role=Role.MEMBER
        )
        TaskNote.objects.create(
            task=task_read_only, author=active_user_read_only, note="This is an important note"
        )

        task_read_only.delete()

        assert TaskNote.objects.count() == 0
