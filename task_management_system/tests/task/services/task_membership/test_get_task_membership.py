import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.test import utils
from rest_framework.exceptions import NotFound
from task.errors import PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP, TASK_MEMBERSHIP_DOES_NOT_EXIST
from task.policies import TaskMembershipPolicy
from task.services import TaskMembershipService
from tests.utils import assert_log


@pytest.mark.django_db
class TestGetMembership:
    def test_success(self, member_is_owner, caplog_loguru, monkeypatch):
        monkeypatch.setattr(TaskMembershipPolicy, "can_view", lambda *a, **k: True)

        actor, actor_membership = member_is_owner
        result = TaskMembershipService.get_task_membership(actor, actor_membership.id)

        assert result is not None
        assert result.id == actor_membership.id

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor can view this task membership.",
            "DEBUG",
            membership=actor_membership.id,
            task=actor_membership.task.id,
        )

    def test_not_found(self, member_is_owner, caplog_loguru, monkeypatch):
        actor, actor_membership = member_is_owner
        actor_membership_id = actor_membership.id
        actor_membership.delete()

        monkeypatch.setattr(TaskMembershipPolicy, "can_view", lambda *a, **k: True)

        with pytest.raises(NotFound) as exc:
            TaskMembershipService.get_task_membership(actor, actor_membership_id)
        assert TASK_MEMBERSHIP_DOES_NOT_EXIST == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Not found: Task membership not found.",
            "WARNING",
            membership=actor_membership_id,
        )

    def test_permission_denied(self, member_is_owner, caplog_loguru, monkeypatch):
        actor, actor_membership = member_is_owner

        monkeypatch.setattr(TaskMembershipPolicy, "can_view", lambda *a, **k: False)

        with pytest.raises(PermissionDenied) as exc:
            TaskMembershipService.get_task_membership(actor, actor_membership.id)
        assert PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: Actor cannot view the task membership.",
            "WARNING",
            membership=actor_membership.id,
            task=actor_membership.task.id,
        )

    def test_is_efficient(self, member_is_owner, monkeypatch):
        actor, actor_membership = member_is_owner

        monkeypatch.setattr(TaskMembershipPolicy, "can_view", lambda *args, **kwargs: True)

        with utils.CaptureQueriesContext(connection) as queries:
            TaskMembershipService.get_task_membership(actor, actor_membership.id)
        assert len(queries) <= 3
