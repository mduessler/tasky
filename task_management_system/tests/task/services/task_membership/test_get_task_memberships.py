import pytest
from django.core.exceptions import PermissionDenied
from task.errors import PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP
from task.models import TaskMembership
from task.services import TaskMembershipService
from tests.utils import assert_log


@pytest.mark.django_db
class TestGetTaskMemberships:
    def test_success(self, superuser, task_memberships, caplog_loguru):
        result = TaskMembershipService.get_task_memberships(superuser)

        assert result.count() == TaskMembership.objects.all().count()

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission granted: Actor can view all memberships.", "DEBUG")

    def test_permission_denied(self, member_is_owner, caplog_loguru):
        actor, _ = member_is_owner

        with pytest.raises(PermissionDenied) as exc:
            TaskMembershipService.get_task_memberships(actor)
        assert PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP == str(exc.value)

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Permission denied: Actor can not view all memberships.", "WARNING")
