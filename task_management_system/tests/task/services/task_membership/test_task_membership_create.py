import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_CREATE_TASK_MEMBERSHIP
from task.models import Role, TaskMembership
from task.policies import TaskMembershipPolicy
from task.services import TaskMembershipService
from tests.utils import assert_log


@pytest.mark.django_db
class TestCreate:
    def test_success(self, member_is_owner, task, user_is_not_member, caplog_loguru, monkeypatch):
        actor, _ = member_is_owner
        user, _ = user_is_not_member
        data = {"task": task, "user": user, "role": Role.MEMBER}

        monkeypatch.setattr(TaskMembershipPolicy, "can_create", lambda *a, **k: True)

        membership = TaskMembershipService.create(actor, data)

        assert membership is not None
        assert membership.user == user
        assert membership.task == task
        assert membership.role == Role.MEMBER

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Success: Task membership created.",
            "DEBUG",
            membership=membership.id,
            task=task.id,
        )

    def test_permission_denied_no_privileges(
        self, member_is_member, task, user_is_not_member, monkeypatch, caplog_loguru
    ):
        actor, _ = member_is_member
        user, _ = user_is_not_member
        data = {"task": task, "user": user, "role": Role.MEMBER}

        monkeypatch.setattr(TaskMembershipPolicy, "can_create", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskMembershipService.create(actor, data)
        assert PERMISSION_DENIED_TO_CREATE_TASK_MEMBERSHIP == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor cannot create a membership for task.",
            "WARNING",
            task=task.id,
        )

    def test_validation_error(self, member_is_owner, task, monkeypatch, caplog_loguru):
        def mock_full_clean(self, *a, **k):
            raise ValidationError("Error")

        actor, _ = member_is_owner
        data = {"task": task, "user": actor, "role": Role.MEMBER}

        monkeypatch.setattr(TaskMembershipPolicy, "can_create", lambda *a, **k: True)
        monkeypatch.setattr(TaskMembership, "full_clean", mock_full_clean)

        with pytest.raises(ValidationError) as exc:
            TaskMembershipService.create(actor, data)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: can not create task membership. Reason: {exc.value}",
            "WARNING",
            task=task.id,
        )

    def test_integrity_error(
        self, member_is_owner, task, user_is_not_member, caplog_loguru, monkeypatch
    ):
        def mock_full_clean(self, *args, **kwargs):
            raise IntegrityError("Error")

        actor, _ = member_is_owner
        user, _ = user_is_not_member
        data = {"task": task, "user": user, "role": Role.MEMBER}

        monkeypatch.setattr(TaskMembershipPolicy, "can_create", lambda *a, **k: True)
        monkeypatch.setattr(TaskMembership, "full_clean", mock_full_clean)

        with pytest.raises(IntegrityError) as exc:
            TaskMembershipService.create(actor, data)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: can not create task membership. Reason: {exc.value}",
            "WARNING",
            task=task.id,
        )

    def test_atomicity_on_error(self, member_is_owner, task, user_is_not_member, monkeypatch):
        def mock_save(self, *a, **k):
            raise IntegrityError("Error")

        actor, _ = member_is_owner
        user, _ = user_is_not_member
        cnt = TaskMembership.objects.count()

        monkeypatch.setattr(TaskMembershipPolicy, "can_create", lambda *a, **k: True)
        monkeypatch.setattr(TaskMembership, "save", mock_save)

        with pytest.raises(IntegrityError):
            TaskMembershipService.create(actor, {"task": task, "user": user, "role": Role.MEMBER})
        assert TaskMembership.objects.count() == cnt

    def test_is_efficient(self, member_is_owner, user_is_not_member, task, monkeypatch):
        actor, _ = member_is_owner
        user, _ = user_is_not_member

        monkeypatch.setattr(TaskMembershipPolicy, "can_create", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskMembershipService.create(actor, {"task": task, "user": user, "role": Role.MEMBER})
        assert len(queries) <= 12
