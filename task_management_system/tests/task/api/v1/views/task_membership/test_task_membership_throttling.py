from __future__ import annotations

import pytest
from task.api.v1.serializers import TaskMembershipWriteSerializer
from task.api.v1.throttling import (
    TaskMembershipDeleteBurst,
    TaskMembershipDeleteSustained,
    TaskMembershipReadBurst,
    TaskMembershipReadSustained,
    TaskMembershipUpdateBurst,
    TaskMembershipUpdateSustained,
)
from task.services import TaskMembershipService
from tests.utils import (
    assert_burst_throttle,
    assert_sustained_throttle,
    parse_url,
)

BASENAME = "membership"


@pytest.mark.django_db
class TestThrottling:
    def test_read_burst_throttle(self, superuser_read_only, api_client):
        assert_burst_throttle(
            superuser_read_only,
            parse_url(BASENAME, "list"),
            "get",
            api_client,
            "task_membership_read",
            2,
            100,
            TaskMembershipReadBurst,
            TaskMembershipReadSustained,
        )

    def test_read_sustained_throttle(self, superuser_read_only, api_client):
        assert_sustained_throttle(
            superuser_read_only,
            parse_url(BASENAME, "list"),
            "get",
            api_client,
            "task_membership_read",
            100,
            2,
            TaskMembershipReadBurst,
            TaskMembershipReadSustained,
        )

    def test_delete_burst_throttle(
        self, superuser_read_only, task_membership_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(TaskMembershipService, "delete", lambda a, m: None)

        assert_burst_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_membership_read_only.id),
            "delete",
            api_client,
            "task_membership_delete",
            2,
            100,
            TaskMembershipDeleteBurst,
            TaskMembershipDeleteSustained,
        )

    def test_delete_sustained_throttle(
        self, superuser_read_only, task_membership_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(TaskMembershipService, "delete", lambda a, m: None)

        assert_sustained_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_membership_read_only.id),
            "delete",
            api_client,
            "task_membership_delete",
            100,
            2,
            TaskMembershipDeleteBurst,
            TaskMembershipDeleteSustained,
        )

    def test_update_burst_throttle(
        self, superuser_read_only, task_membership_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(
            TaskMembershipWriteSerializer, "save", lambda s: task_membership_read_only
        )

        assert_burst_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_membership_read_only.id),
            "patch",
            api_client,
            "task_membership_update",
            2,
            100,
            TaskMembershipUpdateBurst,
            TaskMembershipUpdateSustained,
        )

    def test_update_sustained_throttle(
        self, superuser_read_only, task_membership_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(
            TaskMembershipWriteSerializer, "save", lambda s: task_membership_read_only
        )

        assert_sustained_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_membership_read_only.id),
            "patch",
            api_client,
            "task_membership_update",
            100,
            2,
            TaskMembershipUpdateBurst,
            TaskMembershipUpdateSustained,
        )
