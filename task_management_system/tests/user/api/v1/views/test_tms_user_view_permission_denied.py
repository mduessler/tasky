from __future__ import annotations

import pytest
from tests.utils import parse_url
from user.errors import (
    PERMISSION_DENIED_TO_DELETE_USER,
    PERMISSION_DENIED_TO_UPDATE_USER,
    PERMISSION_DENIED_TO_VIEW_USER,
)
from user.policies import TmsUserPolicy

BASENAME = "user"


@pytest.mark.django_db
class TestPermissionDenied:
    def test_list(self, inactive_user_read_only, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda a, u: False)

        api_client.force_authenticate(user=inactive_user_read_only)
        response = api_client.get(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == PERMISSION_DENIED_TO_VIEW_USER

    def test_retrieve(
        self, inactive_user_read_only, active_user_read_only, api_client, monkeypatch
    ):
        url = parse_url(BASENAME, "detail", active_user_read_only.id)

        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda a, u: False)

        api_client.force_authenticate(user=inactive_user_read_only)
        response = api_client.get(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == PERMISSION_DENIED_TO_VIEW_USER

    def test_patch(self, inactive_user_read_only, active_user_read_only, api_client, monkeypatch):
        data = {"username": "XoXoXo"}
        url = parse_url(BASENAME, "detail", active_user_read_only.id)

        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda a, u: True)
        monkeypatch.setattr(TmsUserPolicy, "can_update", lambda a, u, r: False)

        api_client.force_authenticate(user=inactive_user_read_only)
        response = api_client.patch(url, data=data)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == PERMISSION_DENIED_TO_UPDATE_USER

    def test_delete(self, inactive_user_read_only, active_user_read_only, api_client, monkeypatch):
        url = parse_url(BASENAME, "detail", active_user_read_only.id)

        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda a, u: True)
        monkeypatch.setattr(TmsUserPolicy, "can_delete", lambda a, u: False)

        api_client.force_authenticate(user=inactive_user_read_only)
        response = api_client.delete(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == PERMISSION_DENIED_TO_DELETE_USER

    @pytest.mark.parametrize(
        "url_name",
        [
            "tasks",
            "task-memberships",
            "task-notes",
        ],
    )
    def test_related_objects(
        self, url_name, inactive_user_read_only, active_user_read_only, api_client, monkeypatch
    ):
        url = parse_url(BASENAME, url_name, active_user_read_only.id)

        monkeypatch.setattr(TmsUserPolicy, "can_view", lambda a, u: False)

        api_client.force_authenticate(user=inactive_user_read_only)
        response = api_client.get(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == PERMISSION_DENIED_TO_VIEW_USER
