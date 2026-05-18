import pytest
from django.core.exceptions import ValidationError
from task.models import Role, TaskMembership, TaskNote


@pytest.mark.django_db
class TestTaskNote:

    def test_create_note_success(self, task, active_user):
        TaskMembership.objects.create(user=active_user, task=task, role=Role.MEMBER)

        note_text = "This is an important note"
        note = TaskNote.objects.create(task=task, author=active_user, note=note_text)

        assert note.pk is not None
        assert note.note == note_text
        assert note.author == active_user

    def test_create_note_author_not_member_raises_error(self, task, active_user):
        with pytest.raises(ValidationError) as excinfo:
            TaskNote.objects.create(
                task=task, author=active_user, note="This is an important note"
            )
        assert "Author must be a member of the task." in str(excinfo.value)

    def test_create_note_without_author_success(self, task):
        note = TaskNote.objects.create(task=task, author=None, note="This is an important note")
        assert note.author is None
        assert note.pk is not None

    def test_note_content_cannot_be_empty(self, task, active_user):
        TaskMembership.objects.create(user=active_user, task=task, role=Role.MEMBER)

        with pytest.raises(ValidationError):
            TaskNote.objects.create(task=task, author=active_user, note="")

    def test_on_delete_set_null_author(self, task, active_user):
        TaskMembership.objects.create(user=active_user, task=task, role=Role.MEMBER)
        note = TaskNote.objects.create(
            task=task, author=active_user, note="This is an important note"
        )

        active_user.delete()
        note.refresh_from_db()

        assert note.author is None
        assert note.note == "This is an important note"

    def test_on_delete_cascade_task(self, task, active_user):
        TaskMembership.objects.create(user=active_user, task=task, role=Role.MEMBER)
        TaskNote.objects.create(task=task, author=active_user, note="This is an important note")

        task.delete()

        assert TaskNote.objects.count() == 0
