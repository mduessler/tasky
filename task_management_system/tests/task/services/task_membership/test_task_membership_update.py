import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_UPDATE_TASK_MEMBERSHIP
from task.models import Role, TaskMembership
from task.policies import TaskMembershipPolicy
from task.services import TaskMembershipService
from tests.utils import assert_log


@pytest.mark.django_db
class TestUpdate:
    def test_success(self, member_is_owner, task_membership, caplog_loguru, monkeypatch):
        actor, actor_membership = member_is_owner
        data = {"role": Role.ADMIN}

        monkeypatch.setattr(TaskMembershipPolicy, "can_update", lambda *a, **k: True)

        updated = TaskMembershipService.update(actor, task_membership.id, data)

        task_membership.refresh_from_db()
        assert updated.role == Role.ADMIN
        assert task_membership.role == Role.ADMIN

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Success: Task membership updated.",
            "DEBUG",
            task=actor_membership.task_id,
            membership=task_membership.id,
        )

    def test_partial_update_does_not_override_other_fields(
        self, member_is_owner, task_membership, monkeypatch
    ):
        actor, _ = member_is_owner
        original_user = task_membership.user
        data = {"role": Role.ADMIN}

        monkeypatch.setattr(TaskMembershipPolicy, "can_update", lambda *a, **k: True)

        TaskMembershipService.update(actor, task_membership.id, data)

        task_membership.refresh_from_db()
        assert task_membership.role == Role.ADMIN
        assert task_membership.user == original_user

    def test_permission_denied_no_privileges(
        self, member_is_member, member_is_owner, monkeypatch, caplog_loguru
    ):
        actor, actor_membership = member_is_owner
        _, membership = member_is_member
        data = {"role": Role.ADMIN}

        monkeypatch.setattr(TaskMembershipPolicy, "can_update", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskMembershipService.update(actor, membership.id, data)
        assert PERMISSION_DENIED_TO_UPDATE_TASK_MEMBERSHIP == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor cannot update the task membership.",
            "WARNING",
            task=actor_membership.task_id,
            membership=membership.id,
        )

    def test_validation_error(self, member_is_owner, member_is_member, monkeypatch, caplog_loguru):
        def mock_full_clean(*args, **kwargs):
            raise ValidationError("Error")

        actor, actor_membership = member_is_owner
        _, membership = member_is_member
        data = {"role": Role.ADMIN}

        monkeypatch.setattr(TaskMembershipPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TaskMembership, "full_clean", mock_full_clean)

        with pytest.raises(ValidationError) as exc:
            TaskMembershipService.update(actor, membership.id, data)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: can not update task membership. Reason: {exc.value}",
            "WARNING",
            task=actor_membership.task_id,
            membership=membership.id,
        )

    def test_integrity_error(self, member_is_owner, member_is_member, monkeypatch, caplog_loguru):
        def mock_full_clean(*args, **kwargs):
            raise IntegrityError("Error")

        actor, _ = member_is_owner
        _, membership = member_is_member
        data = {"role": Role.ADMIN}

        monkeypatch.setattr(TaskMembershipPolicy, "can_update", lambda *a, **k: True)
        monkeypatch.setattr(TaskMembership, "full_clean", mock_full_clean)

        with pytest.raises(IntegrityError) as exc:
            TaskMembershipService.update(actor, membership.id, data)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Validation error: can not update task membership. Reason: {exc.value}",
            "WARNING",
            task=membership.task.id,
            membership=membership.id,
        )

    def test_atomicity_on_error(self, member_is_owner, task_membership, monkeypatch):
        def mock_save(self, *args, **kwargs):
            raise IntegrityError("Error")

        actor, _ = member_is_owner
        original_role = task_membership.role

        monkeypatch.setattr(TaskMembership, "save", mock_save)

        with pytest.raises(IntegrityError):
            TaskMembershipService.update(actor, task_membership.id, {"role": Role.ADMIN})

        task_membership.refresh_from_db()
        assert task_membership.role == original_role

    def test_is_efficient(self, member_is_owner, task_membership, monkeypatch):
        actor, _ = member_is_owner

        monkeypatch.setattr(TaskMembershipPolicy, "can_update", lambda *args, **kwargs: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskMembershipService.update(actor, task_membership.id, {"role": Role.ADMIN})
        assert len(queries) <= 13
