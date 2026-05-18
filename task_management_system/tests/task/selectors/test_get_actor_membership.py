import pytest
from task.models import Task
from task.selectors import get_actor_membership
from tests.utils import assert_log


@pytest.mark.django_db
class TestGetActorMembership:
    @pytest.mark.parametrize(
        "actor_fixture",
        ["member_is_owner", "member_is_admin", "member_is_member", "member_is_viewer"],
    )
    def test_get_actor_membership_db_hit(self, actor_fixture, request, task, caplog_loguru):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        result = get_actor_membership(actor, task)

        assert result == actor_membership

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Membership found via DB query.",
            "DEBUG",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    @pytest.mark.parametrize("actor_fixture", ["superuser_is_not_member", "user_is_not_member"])
    def test_get_actor_membership_no_db_hit(self, actor_fixture, request, task, caplog_loguru):
        actor, _ = request.getfixturevalue(actor_fixture)
        result = get_actor_membership(actor, task)

        assert result is None

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "No membership found via DB query.",
            "DEBUG",
            task=task.id,
        )

    @pytest.mark.parametrize(
        "actor_fixture",
        ["member_is_owner", "member_is_admin", "member_is_member", "member_is_viewer"],
    )
    def test_get_actor_membership_prefetch_hit(self, actor_fixture, request, task, caplog_loguru):
        actor, actor_membership = request.getfixturevalue(actor_fixture)
        task = Task.objects.prefetch_related("memberships").get(id=task.id)
        result = get_actor_membership(actor, task)

        assert result == actor_membership

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Membership found via prefetch.",
            "DEBUG",
            task=task.id,
            actor_membership=actor_membership.id,
        )

    @pytest.mark.parametrize("actor_fixture", ["superuser_is_not_member", "user_is_not_member"])
    def test_get_actor_membership_no_prefetch_hit(
        self, actor_fixture, request, task, caplog_loguru
    ):
        actor, _ = request.getfixturevalue(actor_fixture)
        task = Task.objects.prefetch_related("memberships").get(id=task.id)
        result = get_actor_membership(actor, task)

        assert result is None

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "No membership found in prefetched data.",
            "DEBUG",
            task=task.id,
        )
