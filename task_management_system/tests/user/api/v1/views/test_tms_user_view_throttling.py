from __future__ import annotations

import pytest
from tests.utils import assert_burst_throttle, assert_sustained_throttle, parse_url
from user.api.v1.throttling import (
    TmsUserDeleteBurst,
    TmsUserDeleteSustained,
    TmsUserReadBurst,
    TmsUserReadSustained,
    TmsUserUpdateBurst,
    TmsUserUpdateSustained,
)
from user.services import TmsUserService

BASENAME = "user"


@pytest.mark.django_db
class TestThrottling:
    def test_read_burst_throttle(self, superuser, api_client):
        assert_burst_throttle(
            superuser,
            parse_url(BASENAME, "list"),
            "get",
            api_client,
            "tms_user_read",
            2,
            100,
            TmsUserReadBurst,
            TmsUserReadSustained,
        )

    def test_read_sustained_throttle(self, superuser, api_client):
        assert_sustained_throttle(
            superuser,
            parse_url(BASENAME, "list"),
            "get",
            api_client,
            "tms_user_read",
            100,
            2,
            TmsUserReadBurst,
            TmsUserReadSustained,
        )

    def test_delete_burst_throttle(self, superuser, active_user, api_client, monkeypatch):
        monkeypatch.setattr(TmsUserService, "delete", lambda a, u: None)
        assert_burst_throttle(
            superuser,
            parse_url(BASENAME, "detail", active_user.id),
            "delete",
            api_client,
            "tms_user_delete",
            2,
            100,
            TmsUserDeleteBurst,
            TmsUserDeleteSustained,
        )

    def test_delete_sustained_throttle(self, superuser, active_user, api_client, monkeypatch):
        monkeypatch.setattr(TmsUserService, "delete", lambda a, u: None)
        assert_sustained_throttle(
            superuser,
            parse_url(BASENAME, "detail", active_user.id),
            "delete",
            api_client,
            "tms_user_delete",
            100,
            2,
            TmsUserDeleteBurst,
            TmsUserDeleteSustained,
        )

    def test_update_burst_throttle(self, superuser, active_user, api_client, monkeypatch):
        monkeypatch.setattr(TmsUserService, "update", lambda a, u, r: active_user)
        assert_burst_throttle(
            superuser,
            parse_url(BASENAME, "detail", active_user.id),
            "patch",
            api_client,
            "tms_user_update",
            2,
            100,
            TmsUserUpdateBurst,
            TmsUserUpdateSustained,
        )

    def test_update_sustained_throttle(self, superuser, active_user, api_client, monkeypatch):
        monkeypatch.setattr(TmsUserService, "update", lambda a, u, r: active_user)
        assert_sustained_throttle(
            superuser,
            parse_url(BASENAME, "detail", active_user.id),
            "patch",
            api_client,
            "tms_user_update",
            100,
            2,
            TmsUserUpdateBurst,
            TmsUserUpdateSustained,
        )

    def test_tasks_fallback_throttle(self, superuser, active_user, api_client):
        url = parse_url(BASENAME, "tasks", active_user.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200

    def test_task_memberships_fallback_throttle(self, superuser, active_user, api_client):
        url = parse_url(BASENAME, "task-memberships", active_user.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200

    def test_task_notes_fallback_throttle(self, superuser, active_user, api_client):
        url = parse_url(BASENAME, "task-notes", active_user.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
