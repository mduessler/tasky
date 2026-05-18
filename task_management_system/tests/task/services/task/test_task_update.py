import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection
from django.test import utils
from rest_framework.exceptions import NotFound
from task.errors import CAN_NOT_REOPEN_COMPLETE_TASK, PERMISSION_DENIED_TO_UPDATE_TASK
from task.models import Task
from task.policies import TaskPolicy
from task.services import TaskService
from tests.utils import assert_log


@pytest.mark.django_db
class TestUpdate:
    def test_success(self, member_is_owner, task, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner
        task_id = task.id
        data = {"title": "An important project", "description": "This project is very important."}

        monkeypatch.setattr(TaskPolicy, "can_update", lambda *a, **k: True)

        updated_task = TaskService.update(actor, task_id, data)

        task.refresh_from_db()
        assert updated_task.title == "An important project"
        assert task.title == "An important project"
        assert task.description == "This project is very important."

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Success: Task updated.", "DEBUG", task=task_id)

    def test_not_found(self, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner
        non_existent_id = 9999

        with pytest.raises(NotFound):
            TaskService.update(actor, non_existent_id, {"title": "An important project"})

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Not found: Task not found.", "WARNING", task=non_existent_id)

    def test_permission_denied(self, user_is_not_member, task, caplog_loguru, monkeypatch):
        actor, _ = user_is_not_member
        task_id = task.id

        monkeypatch.setattr(TaskPolicy, "can_update", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskService.update(actor, task_id, {"title": "An important project"})
        assert PERMISSION_DENIED_TO_UPDATE_TASK == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record, "Permission denied: Actor cannot update the tasks", "WARNING", task=task_id
        )

    def test_validation_error(self, member_is_owner, task, caplog_loguru, monkeypatch):
        def mock_full_clean(self):
            raise ValidationError("Error")

        actor, _ = member_is_owner
        task_id = task.id

        monkeypatch.setattr(TaskPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(Task, "full_clean", mock_full_clean)

        with pytest.raises(ValidationError) as exc:
            TaskService.update(actor, task_id, {"title": "An important project"})

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: can not update task. Reason: {exc.value}",
            "WARNING",
            task=task_id,
        )

    def test_integrity_error(self, member_is_owner, task, caplog_loguru, monkeypatch):
        def mock_save(self, *args, **kwargs):
            raise IntegrityError("Error")

        actor, _ = member_is_owner
        task_id = task.id

        monkeypatch.setattr(TaskPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(Task, "save", mock_save)

        with pytest.raises(IntegrityError) as exc:
            TaskService.update(actor, task_id, {"title": "An important project"})

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: can not update task. Reason: {exc.value}",
            "WARNING",
            task=task_id,
        )

    def test_empty_data(self, member_is_owner, task, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner
        task_id = task.id
        update_data = {}

        monkeypatch.setattr(TaskPolicy, "can_update", lambda *a, **k: True)

        with pytest.raises(ValidationError) as exc:
            TaskService.update(actor, task_id, update_data)
        assert "Validation error: Task update failed." == exc.value.messages[0]

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Validation error: Not allowed to update 0 fields.",
            "WARNING",
            task=task_id,
        )

    def test_failure_reopen_complete_task(self, member_is_owner, task, caplog_loguru, monkeypatch):
        task.status = "done"
        task.save()
        task_id = task.id

        actor, _ = member_is_owner
        data = {"status": "doing"}

        monkeypatch.setattr(TaskPolicy, "can_update", lambda *a, **k: True)

        with pytest.raises(ValidationError) as exc:
            TaskService.update(actor, task_id, data)
        assert CAN_NOT_REOPEN_COMPLETE_TASK == str(exc.value.messages[0])

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Validation error: Can not reopen an already closed task.",
            "WARNING",
            task=task_id,
        )

    def test_atomicity_on_error(self, member_is_owner, task, monkeypatch):
        def mock_save(self, *args, **kwargs):
            raise IntegrityError("Error")

        actor, _ = member_is_owner
        task_id = task.id
        original_title = task.title

        monkeypatch.setattr(TaskPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(Task, "save", mock_save)

        with pytest.raises(IntegrityError):
            TaskService.update(actor, task_id, {"title": "An important project"})

        task.refresh_from_db()
        assert task.title == original_title

    def test_partial_update(self, member_is_owner, task, monkeypatch):
        actor, _ = member_is_owner
        task_id = task.id
        original_description = task.description

        monkeypatch.setattr(TaskPolicy, "can_update", lambda *a, **k: True)

        TaskService.update(actor, task_id, {"title": "An important project"})

        task.refresh_from_db()
        assert task.title == "An important project"
        assert task.description == original_description

    def test_is_efficient(self, member_is_owner, task, monkeypatch):
        actor, _ = member_is_owner
        task_id = task.id
        data = {"title": "An important project", "description": "This project is very important."}

        monkeypatch.setattr(TaskPolicy, "can_update", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskService.update(actor, task_id, data)
        assert len(queries) <= 4
        assert any("FOR UPDATE" in q["sql"] for q in queries)
