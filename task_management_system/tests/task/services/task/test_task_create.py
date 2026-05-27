import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_CREATE_TASK
from task.models import Role, Task, TaskMembership
from task.policies import TaskPolicy
from task.services import TaskService
from tests.utils import assert_log


@pytest.mark.django_db
class TestCreate:
    def test_success(self, user_is_not_member, caplog_loguru, monkeypatch):
        actor, _ = user_is_not_member
        data = {"title": "An important project", "description": "This project is very important."}
        task = TaskService.create(actor, data)

        monkeypatch.setattr(TaskPolicy, "can_create", lambda *a, **k: True)

        db_task = Task.objects.get(pk=task.id)

        assert db_task.title == "An important project"
        assert db_task.description == "This project is very important."

        membership = TaskMembership.objects.filter(user=actor, task=task, role=Role.OWNER).first()

        assert membership is not None

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Success: Task created.",
            "DEBUG",
            task=task.id,
            actor_membership=membership.id,
        )

    def test_permission_denied(self, user_is_not_member, caplog_loguru, monkeypatch):
        cnt_tasks = Task.objects.count()
        cnt_tasks_membership = TaskMembership.objects.count()
        actor, _ = user_is_not_member
        data = {"title": "An important project", "description": "This project is very important."}

        monkeypatch.setattr(TaskPolicy, "can_create", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskService.create(actor, data)
        assert PERMISSION_DENIED_TO_CREATE_TASK == str(exc.value)
        assert Task.objects.count() == cnt_tasks
        assert TaskMembership.objects.count() == cnt_tasks_membership

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission denied: Actor cannot create a tasks", "WARNING")

    def test_validation_error(self, user_is_not_member, caplog_loguru, monkeypatch):
        def mock_full_clean(self):
            raise ValidationError("Error")

        cnt_tasks = Task.objects.count()
        cnt_tasks_membership = TaskMembership.objects.count()
        actor, _ = user_is_not_member
        data = {"title": "An important project", "description": "This project is very important."}

        monkeypatch.setattr(TaskPolicy, "can_create", lambda *a, **k: True)
        monkeypatch.setattr(Task, "full_clean", mock_full_clean)

        with pytest.raises(ValidationError) as exc:
            TaskService.create(actor, data)
        assert Task.objects.count() == cnt_tasks
        assert TaskMembership.objects.count() == cnt_tasks_membership

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, f"Validation error: can not create task. Reason: {exc.value}", "WARNING"
        )

    def test_integrity_error(self, user_is_not_member, caplog_loguru, monkeypatch):
        def mock_save(self, *a, **k):
            raise IntegrityError("Error")

        cnt_tasks = Task.objects.count()
        cnt_tasks_membership = TaskMembership.objects.count()
        actor, _ = user_is_not_member
        data = {"title": "An important project", "description": "This project is very important."}

        monkeypatch.setattr(TaskPolicy, "can_create", lambda *a, **k: True)
        monkeypatch.setattr(Task, "save", mock_save)

        with pytest.raises(IntegrityError) as exc:
            TaskService.create(actor, data)
        assert Task.objects.count() == cnt_tasks
        assert TaskMembership.objects.count() == cnt_tasks_membership

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, f"Validation error: can not create task. Reason: {exc.value}", "WARNING"
        )

    def test_membership_validation_error(self, user_is_not_member, caplog_loguru, monkeypatch):
        def mock_full_clean(self, *a, **k):
            raise ValidationError("Error")

        cnt_tasks = Task.objects.count()
        cnt_tasks_membership = TaskMembership.objects.count()
        actor, _ = user_is_not_member
        data = {"title": "An important project", "description": "This project is very important."}

        monkeypatch.setattr(TaskPolicy, "can_create", lambda *a, **k: True)
        monkeypatch.setattr(TaskMembership, "full_clean", mock_full_clean)

        with pytest.raises(ValidationError) as exc:
            TaskService.create(actor, data)
        assert Task.objects.count() == cnt_tasks
        assert TaskMembership.objects.count() == cnt_tasks_membership

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, f"Validation error: can not create task. Reason: {exc.value}", "WARNING"
        )

    def test_atomicity_on_error(self, user_is_not_member, caplog_loguru, monkeypatch):
        def mock_save(self, *a, **k):
            raise IntegrityError("Error")

        cnt_tasks = Task.objects.count()
        cnt_tasks_membership = TaskMembership.objects.count()
        actor, _ = user_is_not_member
        data = {"title": "An important project", "description": "This project is very important."}

        monkeypatch.setattr(TaskPolicy, "can_create", lambda *a, **k: True)
        monkeypatch.setattr(TaskMembership, "save", mock_save)

        with pytest.raises(IntegrityError) as exc:
            TaskService.create(actor, data)
        assert Task.objects.count() == cnt_tasks
        assert TaskMembership.objects.count() == cnt_tasks_membership

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, f"Validation error: can not create task. Reason: {exc.value}", "WARNING"
        )

    def test_is_efficient(self, member_is_owner, monkeypatch):
        actor, _ = member_is_owner
        data = {"title": "An important project", "description": "This project is very important."}

        monkeypatch.setattr(TaskPolicy, "can_create", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskService.create(actor, data)
        assert len(queries) <= 12
