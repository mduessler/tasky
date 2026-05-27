import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection
from django.db.models.deletion import ProtectedError
from django.test import utils
from task.errors import PERMISSION_DENIED_TO_DELETE_TASK_MEMBERSHIP
from task.models import TaskMembership
from task.policies import TaskMembershipPolicy
from task.services import TaskMembershipService
from tests.utils import assert_log


@pytest.mark.django_db
class TestDelete:
    def test_success(self, member_is_owner, member_is_member, caplog_loguru, monkeypatch):
        actor, actor_membership = member_is_owner
        _, membership = member_is_member
        membership_id = membership.id

        monkeypatch.setattr(TaskMembershipPolicy, "can_delete", lambda *a, **k: True)

        TaskMembershipService.delete(actor, membership.id)

        assert not TaskMembership.objects.filter(id=membership_id).exists()

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Success: Task membership deleted.",
            "DEBUG",
            task=actor_membership.task_id,
            membership=membership_id,
        )

    def test_permission_denied_no_privileges(
        self, member_is_member, member_is_owner, monkeypatch, caplog_loguru
    ):
        actor, actor_membership = member_is_member
        _, membership = member_is_owner

        monkeypatch.setattr(TaskMembershipPolicy, "can_delete", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskMembershipService.delete(actor, membership.id)
        assert PERMISSION_DENIED_TO_DELETE_TASK_MEMBERSHIP == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor cannot delete the membership.",
            "WARNING",
            task=actor_membership.task_id,
            membership=membership.id,
        )

    def test_validation_error(self, member_is_owner, member_is_member, monkeypatch, caplog_loguru):
        def mock_delete(*args, **kwargs):
            raise ProtectedError("Error", [])

        actor, _ = member_is_owner
        _, membership = member_is_member

        monkeypatch.setattr(TaskMembershipPolicy, "can_delete", lambda *a, **k: True)
        monkeypatch.setattr(TaskMembership, "delete", mock_delete)

        with pytest.raises(ValidationError):
            TaskMembershipService.delete(actor, membership.id)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Protected error: Task membership deletion failed.",
            "ERROR",
            task=membership.task.id,
            membership=membership.id,
        )

    def test_atomicity_on_error(self, member_is_owner, member_is_member, monkeypatch):
        def mock_delete(*args, **kwargs):
            raise ProtectedError("Error", [])

        actor, _ = member_is_owner
        _, task_membership = member_is_member
        membership_id = task_membership.id

        monkeypatch.setattr(TaskMembershipPolicy, "can_create", lambda *a, **k: True)
        monkeypatch.setattr(TaskMembership, "delete", mock_delete)

        with pytest.raises(ValidationError):
            TaskMembershipService.delete(actor, task_membership.id)
        assert TaskMembership.objects.filter(id=membership_id).exists()

    def test_is_efficient(self, member_is_owner, member_is_member, monkeypatch):
        actor, _ = member_is_owner
        _, task_membership = member_is_member

        monkeypatch.setattr(TaskMembershipPolicy, "can_create", lambda *a, **k: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskMembershipService.delete(actor, task_membership.id)
        assert len(queries) <= 6
