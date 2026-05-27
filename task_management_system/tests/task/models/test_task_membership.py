import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from task.models import Role, TaskMembership


@pytest.mark.django_db
class TestTaskMembership:

    def test_create_membership_success(self, task_read_only, active_user_read_only):
        membership = TaskMembership.objects.create(
            user=active_user_read_only, task=task_read_only, role=Role.MEMBER
        )
        assert membership.role == Role.MEMBER
        assert str(membership) == f"{active_user_read_only.pk} - {task_read_only.pk} (member)"

    def test_unique_user_task_constraint(self, task_read_only, active_user_read_only):
        TaskMembership.objects.create(
            user=active_user_read_only, task=task_read_only, role=Role.MEMBER
        )

        with pytest.raises(ValidationError):
            TaskMembership.objects.create(
                user=active_user_read_only, task=task_read_only, role=Role.VIEWER
            )

    def test_only_one_owner_per_task(self, task_read_only, active_user_read_only):
        TaskMembership.objects.create(
            user=active_user_read_only, task=task_read_only, role=Role.OWNER
        )
        with pytest.raises(ValidationError):
            TaskMembership.objects.create(
                user=active_user_read_only, task=task_read_only, role=Role.OWNER
            )

    def test_multiple_members_allowed(
        self, task_read_only, active_user_read_only, superuser_read_only
    ):
        cnt = TaskMembership.objects.filter(task=task_read_only).count()
        TaskMembership.objects.create(
            user=active_user_read_only, task=task_read_only, role=Role.MEMBER
        )
        TaskMembership.objects.create(
            user=superuser_read_only, task=task_read_only, role=Role.MEMBER
        )

        assert TaskMembership.objects.filter(task=task_read_only).count() == cnt + 2

    def test_invalid_role_raises_error(self, task_read_only, active_user_read_only):
        with pytest.raises(ValidationError) as excinfo:
            TaskMembership.objects.create(
                user=active_user_read_only, task=task_read_only, role="GHT"
            )
        assert "role" in excinfo.value.message_dict

    def test_get_user_role_utility(self, task_read_only, active_user_read_only):
        TaskMembership.objects.create(
            user=active_user_read_only, task=task_read_only, role=Role.ADMIN
        )

        assert TaskMembership.get_user_role(active_user_read_only, task_read_only) == Role.ADMIN
        assert TaskMembership.get_user_role(None, task_read_only) is None

    def test_integrity_error_on_db_level(self, task_read_only, active_user_read_only):
        TaskMembership.objects.create(
            user=active_user_read_only, task=task_read_only, role=Role.MEMBER
        )
        duplicate_membership = TaskMembership(
            user=active_user_read_only, task=task_read_only, role=Role.VIEWER
        )

        with pytest.raises(IntegrityError):
            duplicate_membership.save(skip_validation=True)
