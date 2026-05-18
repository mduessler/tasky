from __future__ import annotations

import pytest
from task.api.v1.permissions import TaskPermission
from task.policies import TaskMembershipPolicy, TaskNotePolicy, TaskPolicy
from tests.task.api.v1.views.utils import select_data_dict
from tests.utils import parse_url

BASENAME = "task"


@pytest.mark.django_db
class TestHttpMethods:
    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
        ],
    )
    @pytest.mark.parametrize(
        "method, expected, url_name",
        [
            ("get", 200, "list"),
            ("post", 201, "list"),
            ("options", 200, "list"),
            ("head", 200, "list"),
            ("get", 200, "detail"),
            ("patch", 200, "detail"),
            ("delete", 204, "detail"),
            ("get", 200, "memberships"),
            ("post", 201, "membership"),
            ("get", 200, "notes"),
            ("post", 201, "note"),
        ],
    )
    def test_allowed(
        self,
        method,
        expected,
        url_name,
        actor_fixture,
        request,
        task,
        data_task,
        data_task_membership,
        data_task_note_author_is_member,
        api_client,
        monkeypatch,
    ):
        actor, _ = request.getfixturevalue(actor_fixture)

        url = parse_url(BASENAME, url_name, task.id)
        data = select_data_dict(
            method, url_name, data_task, data_task_membership, data_task_note_author_is_member
        )

        monkeypatch.setattr(TaskPermission, "has_permission", lambda s, r, v: True)
        monkeypatch.setattr(TaskPermission, "has_object_permission", lambda s, r, v, t: True)
        monkeypatch.setattr(TaskPolicy, "can_access", lambda a: True)
        monkeypatch.setattr(TaskPolicy, "can_create", lambda a: True)
        monkeypatch.setattr(TaskPolicy, "can_view", lambda a, t: True)
        monkeypatch.setattr(TaskPolicy, "can_view_tasks", lambda a: True)
        monkeypatch.setattr(TaskPolicy, "can_update", lambda a, t, r: True)
        monkeypatch.setattr(TaskPolicy, "can_delete", lambda a, t: True)

        monkeypatch.setattr(TaskMembershipPolicy, "can_create", lambda a, t: True)
        monkeypatch.setattr(TaskPolicy, "can_view_memberships_of_task", lambda a, t: True)

        monkeypatch.setattr(TaskNotePolicy, "can_create", lambda a, t: True)
        monkeypatch.setattr(TaskPolicy, "can_view_notes_of_task", lambda a, t: True)

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
    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("put", "detail"),
        ],
    )
    def test_forbidden(
        self, actor_fixture, method, url_name, request, task, data_task, api_client
    ):
        actor, _ = request.getfixturevalue(actor_fixture)

        url = parse_url(BASENAME, url_name, task.id)

        api_client.force_authenticate(user=actor)
        response = getattr(api_client, method)(url, data=data_task)

        assert response.status_code == 403
