from __future__ import annotations

import pytest
from task.errors import (
    PERMISSION_DENIED_TO_DELETE_TASK_NOTE,
    PERMISSION_DENIED_TO_UPDATE_TASK_NOTE,
    PERMISSION_DENIED_TO_VIEW_TASK_NOTE,
)
from task.policies import TaskNotePolicy
from tests.utils import parse_url

BASENAME = "note"


@pytest.mark.django_db
class TestPermissionDenied:
    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "user_is_not_member",
        ],
    )
    def test_list_actor_has_no_permission(self, actor_fixture, request, task_notes, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)

        url = parse_url(BASENAME, "list")

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) in {
            "You do not have permission to perform this action.",
            PERMISSION_DENIED_TO_VIEW_TASK_NOTE,
        }

    def test_retrieve_actor_has_no_permission(
        self, user_is_not_member, task_note, api_client, monkeypatch
    ):
        actor, _ = user_is_not_member
        url = parse_url(BASENAME, "detail", task_note.id)

        monkeypatch.setattr(TaskNotePolicy, "can_view", lambda a, n: False)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == "You do not have permission to perform this action."

    @pytest.mark.parametrize(
        "actor_fixture", ["member_is_member", "member_is_viewer", "user_is_not_member"]
    )
    def test_patch_actor_has_no_permission(
        self, actor_fixture, request, task_note, api_client, monkeypatch
    ):
        actor, _ = request.getfixturevalue(actor_fixture)

        data = {"note": "updated note"}
        url = parse_url(BASENAME, "detail", task_note.id)

        monkeypatch.setattr(TaskNotePolicy, "can_view", lambda a, n: True)

        api_client.force_authenticate(user=actor)
        response = api_client.patch(url, data=data)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) in {
            "You do not have permission to perform this action.",
            PERMISSION_DENIED_TO_UPDATE_TASK_NOTE,
        }

    @pytest.mark.parametrize(
        "actor_fixture", ["member_is_member", "member_is_viewer", "user_is_not_member"]
    )
    def test_delete_actor_has_no_permission(
        self, actor_fixture, request, task_note, api_client, monkeypatch
    ):
        actor, _ = request.getfixturevalue(actor_fixture)

        url = parse_url(BASENAME, "detail", task_note.id)

        monkeypatch.setattr(TaskNotePolicy, "can_view", lambda a, n: True)

        api_client.force_authenticate(user=actor)
        response = api_client.delete(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) in {
            "You do not have permission to perform this action.",
            PERMISSION_DENIED_TO_DELETE_TASK_NOTE,
        }
