from __future__ import annotations

import pytest
from task.api.v1.permissions import TaskNotePermission
from task.policies import TaskNotePolicy
from tests.utils import parse_url

BASENAME = "note"


@pytest.mark.django_db
class TestHttpMethods:
    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "superuser_is_not_member",
            "user_is_not_member",
        ],
    )
    @pytest.mark.parametrize(
        "method, expected, url_name",
        [
            ("get", 200, "list"),
            ("options", 200, "list"),
            ("head", 200, "list"),
            ("get", 200, "detail"),
            ("patch", 200, "detail"),
            ("delete", 204, "detail"),
        ],
    )
    def test_allowed(
        self,
        method,
        expected,
        url_name,
        actor_fixture,
        request,
        task_note,
        api_client,
        monkeypatch,
    ):
        actor, _ = request.getfixturevalue(actor_fixture)

        data = {"note": "updated note"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, task_note.id)

        monkeypatch.setattr(TaskNotePermission, "has_permission", lambda s, r, v: True)
        monkeypatch.setattr(TaskNotePermission, "has_object_permission", lambda s, r, v, t: True)
        monkeypatch.setattr(TaskNotePolicy, "can_view", lambda a, n: True)
        monkeypatch.setattr(TaskNotePolicy, "can_view_task_notes", lambda a: True)
        monkeypatch.setattr(TaskNotePolicy, "can_update", lambda a, n, d: True)
        monkeypatch.setattr(TaskNotePolicy, "can_delete", lambda a, n: True)

        api_client.force_authenticate(user=actor)
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == expected

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "superuser_is_not_member",
            "user_is_not_member",
        ],
    )
    @pytest.mark.parametrize("method, url_name", [("post", "list"), ("put", "detail")])
    def test_forbidden(
        self,
        actor_fixture,
        method,
        url_name,
        request,
        task_note,
        api_client,
    ):
        actor, _ = request.getfixturevalue(actor_fixture)

        data = {"note": "updated note"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, task_note.id)

        api_client.force_authenticate(user=actor)
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 403
