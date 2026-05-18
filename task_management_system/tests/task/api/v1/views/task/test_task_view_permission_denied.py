from __future__ import annotations

import pytest
from django.urls import reverse
from task.errors import (
    PERMISSION_DENIED_TO_CREATE_TASK_MEMBERSHIP,
    PERMISSION_DENIED_TO_CREATE_TASK_NOTE,
    PERMISSION_DENIED_TO_DELETE_TASK,
    PERMISSION_DENIED_TO_UPDATE_TASK,
    PERMISSION_DENIED_TO_VIEW_TASK,
)
from task.policies import TaskPolicy
from tests.utils import parse_url

BASENAME = "task"


@pytest.mark.django_db
class TestPermissionDenied:
    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "user_is_not_member",
        ],
    )
    def test_list_actor_has_no_permission(self, actor_data, request, api_client, monkeypatch):
        actor, _ = request.getfixturevalue(actor_data)
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr(TaskPolicy, "can_view_tasks", lambda a: False)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == PERMISSION_DENIED_TO_VIEW_TASK

    def test_retrieve_actor_has_no_permission(
        self, user_is_not_member, task, api_client, monkeypatch
    ):
        actor, _ = user_is_not_member
        url = parse_url(BASENAME, "detail", task.id)

        monkeypatch.setattr(TaskPolicy, "can_view", lambda a, t: False)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == PERMISSION_DENIED_TO_VIEW_TASK

    @pytest.mark.parametrize(
        "actor_data",
        ["member_is_admin", "member_is_member", "member_is_viewer", "user_is_not_member"],
    )
    def test_patch_actor_has_no_permission(
        self, actor_data, request, task, api_client, monkeypatch
    ):
        actor, _ = request.getfixturevalue(actor_data)
        url = parse_url(BASENAME, "detail", task.id)
        data = {"title": "updated"}

        monkeypatch.setattr(TaskPolicy, "can_view", lambda a, t: True)

        api_client.force_authenticate(user=actor)
        response = api_client.patch(url, data=data)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == PERMISSION_DENIED_TO_UPDATE_TASK

    @pytest.mark.parametrize(
        "actor_data",
        [
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "user_is_not_member",
        ],
    )
    def test_delete_actor_has_no_permission(
        self, actor_data, request, task, api_client, monkeypatch
    ):
        actor, _ = request.getfixturevalue(actor_data)
        url = parse_url(BASENAME, "detail", task.id)

        monkeypatch.setattr(TaskPolicy, "can_view", lambda a, t: True)

        api_client.force_authenticate(user=actor)
        response = api_client.delete(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == PERMISSION_DENIED_TO_DELETE_TASK

    def test_memberships_actor_has_no_permission(
        self, user_is_not_member, task, api_client, monkeypatch
    ):
        actor, _ = user_is_not_member
        url = reverse(f"{BASENAME}-memberships", args=[task.id])

        monkeypatch.setattr(TaskPolicy, "can_view", lambda a, t: False)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == "You do not have permission to perform this action."

    @pytest.mark.parametrize(
        "actor_data", ["member_is_member", "member_is_viewer", "user_is_not_member"]
    )
    def test_membership_create_actor_has_no_permission(
        self, actor_data, user_is_not_member, request, task, api_client, monkeypatch
    ):
        actor, _ = request.getfixturevalue(actor_data)
        user, _ = user_is_not_member
        url = reverse(f"{BASENAME}-membership", args=[task.id])
        data = {"user_id": user.id, "role": "viewer"}

        monkeypatch.setattr(TaskPolicy, "can_view", lambda a, t: True)

        api_client.force_authenticate(user=actor)
        response = api_client.post(url, data=data)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) in {
            PERMISSION_DENIED_TO_CREATE_TASK_MEMBERSHIP,
            "You do not have permission to perform this action.",
        }

    def test_notes_actor_has_no_permission(
        self, user_is_not_member, task, api_client, monkeypatch
    ):
        actor, _ = user_is_not_member
        url = reverse(f"{BASENAME}-notes", args=[task.id])

        monkeypatch.setattr(TaskPolicy, "can_view", lambda a, t: False)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == "You do not have permission to perform this action."

    @pytest.mark.parametrize("actor_data", ["member_is_viewer", "user_is_not_member"])
    def test_note_create_actor_has_no_permission(
        self, actor_data, request, task, api_client, monkeypatch
    ):
        actor, _ = request.getfixturevalue(actor_data)
        url = reverse(f"{BASENAME}-note", args=[task.id])

        data = {"note": "new task note", "author_id": actor.id}

        monkeypatch.setattr(TaskPolicy, "can_view", lambda a, t: True)

        api_client.force_authenticate(user=actor)
        response = api_client.post(url, data=data)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) in {
            "You do not have permission to perform this action.",
            PERMISSION_DENIED_TO_CREATE_TASK_NOTE,
        }
