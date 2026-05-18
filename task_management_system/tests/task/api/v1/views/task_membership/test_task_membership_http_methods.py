from __future__ import annotations

import pytest
from task.api.v1.permissions import TaskMembershipPermission
from task.policies import TaskMembershipPolicy
from tests.utils import parse_url

BASENAME = "membership"


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
        task_membership,
        api_client,
        monkeypatch,
    ):
        actor, _ = request.getfixturevalue(actor_fixture)
        data = {"role": "viewer"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, task_membership.id)

        monkeypatch.setattr(TaskMembershipPermission, "has_permission", lambda s, r, v: True)
        monkeypatch.setattr(
            TaskMembershipPermission, "has_object_permission", lambda s, r, v, t: True
        )
        monkeypatch.setattr(TaskMembershipPolicy, "can_view", lambda a, m: True)
        monkeypatch.setattr(TaskMembershipPolicy, "can_view_task_memberships", lambda a: True)
        monkeypatch.setattr(TaskMembershipPolicy, "can_update", lambda a, m, r: True)
        monkeypatch.setattr(TaskMembershipPolicy, "can_delete", lambda a, m: True)

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
        [("post", "list"), ("put", "detail")],
    )
    def test_forbidden(
        self,
        actor_fixture,
        method,
        url_name,
        request,
        task_membership,
        api_client,
    ):
        actor, _ = request.getfixturevalue(actor_fixture)
        data = {"role": "viewer"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, task_membership.id)

        api_client.force_authenticate(user=actor)
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 403
