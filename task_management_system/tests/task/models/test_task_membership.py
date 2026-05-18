import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from task.models import Role, TaskMembership


@pytest.mark.django_db
class TestTaskMembership:

    def test_create_membership_success(self, task, active_user):
        membership = TaskMembership.objects.create(user=active_user, task=task, role=Role.MEMBER)
        assert membership.role == Role.MEMBER
        assert str(membership) == f"{active_user.pk} - {task.pk} (member)"

    def test_unique_user_task_constraint(self, task, active_user):
        TaskMembership.objects.create(user=active_user, task=task, role=Role.MEMBER)

        with pytest.raises(ValidationError):
            TaskMembership.objects.create(user=active_user, task=task, role=Role.VIEWER)

    def test_only_one_owner_per_task(self, task, active_user):
        with pytest.raises(ValidationError):
            TaskMembership.objects.create(user=active_user, task=task, role=Role.OWNER)

    def test_multiple_members_allowed(self, task, active_user, superuser):
        cnt = TaskMembership.objects.count()
        TaskMembership.objects.create(user=active_user, task=task, role=Role.MEMBER)
        TaskMembership.objects.create(user=superuser, task=task, role=Role.MEMBER)

        assert TaskMembership.objects.filter(task=task).count() == cnt + 2

    def test_invalid_role_raises_error(self, task, active_user):
        with pytest.raises(ValidationError) as excinfo:
            TaskMembership.objects.create(user=active_user, task=task, role="GHT")
        assert "role" in excinfo.value.message_dict

    def test_get_user_role_utility(self, task, active_user):
        TaskMembership.objects.create(user=active_user, task=task, role=Role.ADMIN)

        assert TaskMembership.get_user_role(active_user, task) == Role.ADMIN
        assert TaskMembership.get_user_role(None, task) is None

    def test_integrity_error_on_db_level(self, task, active_user):
        TaskMembership.objects.create(user=active_user, task=task, role=Role.MEMBER)
        duplicate_membership = TaskMembership(user=active_user, task=task, role=Role.VIEWER)

        with pytest.raises(IntegrityError):
            duplicate_membership.save(skip_validation=True)
