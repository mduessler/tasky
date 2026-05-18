from __future__ import annotations

import pytest
from tests.task.api.v1.views.utils import select_data_dict
from tests.utils import parse_url

BASENAME = "task"


@pytest.mark.django_db
class TestAuthentication:
    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("get", "list"),
            ("post", "list"),
            ("get", "detail"),
            ("patch", "detail"),
            ("delete", "detail"),
            ("get", "memberships"),
            ("post", "membership"),
            ("get", "notes"),
            ("post", "note"),
        ],
    )
    def test_unauthenticated_actor_not_allowed(
        self, method, url_name, task, api_client, data_task, data_task_membership, data_task_note
    ):
        data = select_data_dict(method, url_name, data_task, data_task_membership, data_task_note)
        url = parse_url(BASENAME, url_name, task.id)

        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 401

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
    def test_get_list_permission_denied(self, actor_data, request, superuser, api_client):
        actor, _ = request.getfixturevalue(actor_data)

        url = parse_url(BASENAME, "list")

        api_client.force_authenticate(user=actor)
        response = api_client.get(url, data={"user": superuser.id})

        assert response.status_code == 403

    def test_retrieve_permission_denied(self, user_is_not_member, task, api_client):
        actor, _ = user_is_not_member

        url = parse_url(BASENAME, "detail", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "actor_data", ["member_is_member", "member_is_viewer", "user_is_not_member"]
    )
    def test_patch_permission_denied(self, actor_data, request, task, api_client):
        actor, _ = request.getfixturevalue(actor_data)

        url = parse_url(BASENAME, "detail", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.patch(url, data={"title": "updated"})

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "actor_data",
        ["member_is_admin", "member_is_member", "member_is_viewer", "user_is_not_member"],
    )
    def test_delete_permission_denied(self, actor_data, request, task, api_client):
        actor, _ = request.getfixturevalue(actor_data)

        url = parse_url(BASENAME, "detail", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.delete(url)

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "actor_data", ["member_is_member", "member_is_viewer", "user_is_not_member"]
    )
    def test_membership_create_permission_denied(
        self, actor_data, request, task, superuser, api_client
    ):
        actor, _ = request.getfixturevalue(actor_data)

        url = parse_url(BASENAME, "membership", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.post(url, data={"user_id": superuser.id, "role": "viewer"})

        assert response.status_code == 403

    def test_memberships_view_permission_denied(self, user_is_not_member, task, api_client):
        actor, _ = user_is_not_member

        url = parse_url(BASENAME, "memberships", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403

    @pytest.mark.parametrize("actor_data", ["member_is_viewer", "user_is_not_member"])
    def test_note_create_permission_denied(self, actor_data, request, task, api_client):
        actor, _ = request.getfixturevalue(actor_data)

        url = parse_url(BASENAME, "note", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.post(url, data={"author_id": actor.id, "note": "test"})

        assert response.status_code == 403

    def test_notes_view_permission_denied(self, user_is_not_member, task, api_client):
        actor, _ = user_is_not_member

        url = parse_url(BASENAME, "notes", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("get", "list"),
            ("post", "list"),
            ("get", "detail"),
            ("patch", "detail"),
            ("delete", "detail"),
            ("get", "memberships"),
            ("post", "membership"),
            ("get", "notes"),
            ("post", "note"),
        ],
    )
    def test_expired_token_not_allowed(
        self,
        method,
        url_name,
        superuser,
        task,
        api_client,
        access_token_factory,
        data_task,
        data_task_membership,
        data_task_note,
    ):
        data = select_data_dict(method, url_name, data_task, data_task_membership, data_task_note)
        url = parse_url(BASENAME, url_name, task.id)

        expired_token = access_token_factory(user=superuser, expired=True)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired_token}")
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 401
        assert set(response.data.keys()) == {"code", "detail", "messages"}
        assert str(response.data["detail"]) == "Given token not valid for any token type"

    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("get", "list"),
            ("post", "list"),
            ("get", "detail"),
            ("patch", "detail"),
            ("delete", "detail"),
            ("get", "memberships"),
            ("post", "membership"),
            ("get", "notes"),
            ("post", "note"),
        ],
    )
    def test_invalid_token_not_allowed(
        self, method, url_name, task, api_client, data_task, data_task_membership, data_task_note
    ):
        data = select_data_dict(method, url_name, data_task, data_task_membership, data_task_note)
        url = parse_url(BASENAME, url_name, task.id)

        api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.value")
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 401
        assert set(response.data.keys()) == {"code", "detail", "messages"}
        assert str(response.data["detail"]) == "Given token not valid for any token type"
