import pytest
from task.models import Task
from task.selectors import get_actor_membership
from tests.utils import assert_log


@pytest.mark.django_db
class TestGetActorMembership:
    @pytest.fixture(scope="class", autouse=True)
    def preload(
        self,
        member_is_owner_read_only,
        member_is_admin_read_only,
        member_is_member_read_only,
        member_is_viewer_read_only,
    ):
        pass

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
        ],
    )
    def test_get_actor_membership_db_hit(
        self, actor_fixture, request, task_read_only, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = get_actor_membership(actor, task_read_only)

        assert result == actor_membership

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Membership found via DB query.",
            "DEBUG",
            task=task_read_only.id,
            actor_membership=actor_membership.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture", ["superuser_is_not_member_read_only", "user_is_not_member_read_only"]
    )
    def test_get_actor_membership_no_db_hit(
        self, actor_fixture, request, task_read_only, caplog_loguru
    ):
        actor, _ = request.getfixturevalue(actor_fixture)
        result = get_actor_membership(actor, task_read_only)

        assert result is None

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "No membership found via DB query.",
            "DEBUG",
            task=task_read_only.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
        ],
    )
    def test_get_actor_membership_prefetch_hit(
        self, actor_fixture, request, task_read_only, caplog_loguru
    ):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        task_read_only = Task.objects.prefetch_related("memberships").get(id=task_read_only.id)
        result = get_actor_membership(actor, task_read_only)

        assert result == actor_membership

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Membership found via prefetch.",
            "DEBUG",
            task=task_read_only.id,
            actor_membership=actor_membership.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture", ["superuser_is_not_member_read_only", "user_is_not_member_read_only"]
    )
    def test_get_actor_membership_no_prefetch_hit(
        self, actor_fixture, request, task_read_only, caplog_loguru
    ):
        actor, _ = request.getfixturevalue(actor_fixture)
        task_read_only = Task.objects.prefetch_related("memberships").get(id=task_read_only.id)
        result = get_actor_membership(actor, task_read_only)

        assert result is None

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "No membership found in prefetched data.",
            "DEBUG",
            task=task_read_only.id,
        )
