from __future__ import annotations

import pytest
from task.models import Task, TaskMembership, TaskNote
from tests.user.api.v1.utils import assert_user_response_body
from tests.utils import assert_paginator, extract_results, parse_url
from user.models import TmsUser
from user.services import TmsUserService

BASENAME = "user"


@pytest.mark.django_db
class TestResponseBodyOK:
    def test_list(self, superuser, users, api_client):
        url = parse_url(BASENAME, "list")

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)

        for data in extract_results(response.data):
            user = TmsUser.objects.get(id=data["id"])
            assert_user_response_body(data, user, superuser)

    def test_list_empty_body(self, superuser, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")
        monkeypatch.setattr(TmsUserService, "get_users", lambda s: TmsUser.objects.none())

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)
        assert extract_results(response.data) == []

    def test_retrieve(self, superuser, active_user, api_client):
        url = parse_url(BASENAME, "detail", active_user.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_user_response_body(response.data, active_user, superuser)

    def test_patch(self, superuser, active_user, api_client):
        old_username = active_user.username

        data = {"username": "XoXoXo"}
        url = parse_url(BASENAME, "detail", active_user.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.patch(url, data=data)

        active_user.refresh_from_db()
        assert response.status_code == 200
        assert response.data["username"] != old_username
        assert active_user.username != old_username
        assert_user_response_body(response.data, active_user, superuser)

    def test_delete(self, superuser, active_user, api_client):
        user_id = active_user.id

        url = parse_url(BASENAME, "detail", active_user.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.delete(url)

        assert response.status_code == 204
        assert TmsUser.objects.filter(id=user_id).exists() is False

    def test_tasks(self, superuser, active_user, tasks, api_client):
        url = parse_url(BASENAME, "tasks", active_user.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)

    def test_task_memberships(self, superuser, active_user, task_memberships, api_client):
        url = parse_url(BASENAME, "task-memberships", active_user.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)

    def test_task_notes(self, superuser, active_user, task_notes, api_client):
        url = parse_url(BASENAME, "task-notes", active_user.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)

    def test_tasks_empty_body(self, superuser, active_user, api_client, monkeypatch):
        url = parse_url(BASENAME, "tasks", active_user.id)

        monkeypatch.setattr(TmsUserService, "get_tasks_of_user", lambda a, u: Task.objects.none())

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)
        assert extract_results(response.data) == []

    def test_task_memberships_empty_body(self, superuser, active_user, api_client, monkeypatch):
        url = parse_url(BASENAME, "task-memberships", active_user.id)

        monkeypatch.setattr(
            TmsUserService, "get_memberships_of_user", lambda a, u: TaskMembership.objects.none()
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)
        assert extract_results(response.data) == []

    def test_task_notes_empty_body(self, superuser, active_user, api_client, monkeypatch):
        url = parse_url(BASENAME, "task-notes", active_user.id)

        monkeypatch.setattr(
            TmsUserService, "get_notes_of_user", lambda a, u: TaskNote.objects.none()
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)
        assert extract_results(response.data) == []
