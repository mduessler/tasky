import pytest
from task.models import Role, TaskMembership
from task.policies import TaskMembershipPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestHasPermissionToCreate:
    @pytest.mark.parametrize(
        "actor_fixture", ["member_is_owner_read_only", "member_is_admin_read_only"]
    )
    def test_has_permission_to_create_true(self, actor_fixture, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)

        result = TaskMembershipPolicy.has_permission_to_create(actor)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted. Has permission to create a task membership: True.",
            "DEBUG",
        )

    def test_has_permission_to_create_true_superuser(self, superuser_read_only, caplog_loguru):
        result = TaskMembershipPolicy.has_permission_to_create(superuser_read_only)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted: Actor is superuser and has permission to create membership.",
            "INFO",
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_has_permission_to_create_false(self, actor_fixture, request, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        TaskMembership.objects.filter(user=actor, role__in=[Role.OWNER, Role.ADMIN]).delete()

        result = TaskMembershipPolicy.has_permission_to_create(actor)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission granted. Has permission to create a task membership: False.",
            "DEBUG",
        )

    def test_anonymous_user(self, anonymous_user_read_only, caplog_loguru):
        result = TaskMembershipPolicy.has_permission_to_create(anonymous_user_read_only)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User has not the permission to create a task membersip.",
            "WARNING",
        )

    def test_user_is_None(self, caplog_loguru):
        result = TaskMembershipPolicy.has_permission_to_create(None)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: User has not the permission to create a task membersip.",
            "WARNING",
        )
