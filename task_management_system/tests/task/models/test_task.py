import pytest
from django.core.exceptions import ValidationError
from task.models import Role, Task, TaskMembership, TaskStatus


@pytest.mark.django_db
class TestTask:

    def test_create_task_success(self):
        task = Task.objects.create(
            title="An important project", description="This project is very important."
        )
        assert task.title == "An important project"
        assert task.status == TaskStatus.TODO
        assert task.pk is not None

    def test_title_validation_empty(self):
        with pytest.raises(ValidationError) as excinfo:
            Task.objects.create(title="", description="This project is very important.")
        assert "title" in excinfo.value.message_dict

    def test_title_validation_whitespace(self):
        with pytest.raises(ValidationError) as excinfo:
            Task.objects.create(title="   ", description="This project is very important.")
        assert "Title cannot be empty or whitespace." in str(excinfo.value)

    def test_status_choices_validation(self):
        with pytest.raises(ValidationError):
            Task.objects.create(
                title="An important project",
                status="invalid",
            )

    def test_task_members_relationship(
        self, task_read_only, active_user_read_only, superuser_read_only
    ):
        cnt = TaskMembership.objects.filter(task=task_read_only).count()
        TaskMembership.objects.create(
            user=active_user_read_only, task=task_read_only, role=Role.VIEWER
        )
        TaskMembership.objects.create(
            user=superuser_read_only, task=task_read_only, role=Role.MEMBER
        )

        assert task_read_only.members.count() == cnt + 2
        assert active_user_read_only in task_read_only.members.all()
        assert superuser_read_only in task_read_only.members.all()

    def test_str_representation(self):
        task = Task(title="An important project")
        assert str(task) == "An important project"

    def test_skip_validation_flag(self):
        task = Task(title="", description="This project is very important.")

        task.save(skip_validation=True)

        assert task.pk is not None
        assert task.title == ""
