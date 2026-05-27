from __future__ import annotations

import pytest
from task.models import TaskMembership
from task.services import TaskMembershipService
from tests.task.api.v1.views.utils import assert_task_membership_response_body
from tests.utils import assert_paginator, extract_results, parse_url

BASENAME = "membership"


@pytest.mark.django_db
class TestResponseBodyOK:
    def test_list(self, superuser, task_memberships, api_client):
        url = parse_url(BASENAME, "list")

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)

        for data in extract_results(response.data):
            membership = TaskMembership.objects.get(id=data["id"])
            assert_task_membership_response_body(data, membership, superuser)

    def test_list_empty_body(self, superuser, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr(
            TaskMembershipService,
            "get_task_memberships",
            lambda s: TaskMembership.objects.none(),
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)
        assert extract_results(response.data) == []

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner",
            "member_is_admin",
            "member_is_member",
            "member_is_viewer",
            "superuser_is_not_member",
        ],
    )
    def test_retrieve(self, actor_fixture, request, task_membership, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)
        url = parse_url(BASENAME, "detail", task_membership.id)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_task_membership_response_body(response.data, task_membership, actor)

    @pytest.mark.parametrize(
        "actor_fixture",
        ["member_is_owner", "member_is_admin", "superuser_is_not_member"],
    )
    def test_patch(self, actor_fixture, request, task_membership, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)
        old_role = task_membership.role

        data = {"role": "viewer"}
        url = parse_url(BASENAME, "detail", task_membership.id)

        api_client.force_authenticate(user=actor)
        response = api_client.patch(url, data=data)

        task_membership.refresh_from_db()
        assert response.status_code == 200
        assert task_membership.role is not old_role
        assert_task_membership_response_body(response.data, task_membership, actor)

    @pytest.mark.parametrize(
        "actor_fixture",
        ["member_is_owner", "superuser_is_not_member"],
    )
    def test_delete(self, actor_fixture, request, task_membership, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)
        membership_id = task_membership.id

        url = parse_url(BASENAME, "detail", task_membership.id)

        api_client.force_authenticate(user=actor)
        response = api_client.delete(url)

        assert response.status_code == 204
        assert TaskMembership.objects.filter(id=membership_id).exists() is False
