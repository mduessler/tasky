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

    def test_task_members_relationship(self, task, active_user, superuser):
        cnt = TaskMembership.objects.count()
        TaskMembership.objects.create(user=active_user, task=task, role=Role.VIEWER)
        TaskMembership.objects.create(user=superuser, task=task, role=Role.MEMBER)

        assert task.members.count() == cnt + 2
        assert active_user in task.members.all()
        assert superuser in task.members.all()

    def test_str_representation(self):
        task = Task(title="An important project")
        assert str(task) == "An important project"

    def test_skip_validation_flag(self):
        task = Task(title="", description="This project is very important.")

        task.save(skip_validation=True)

        assert task.pk is not None
        assert task.title == ""
