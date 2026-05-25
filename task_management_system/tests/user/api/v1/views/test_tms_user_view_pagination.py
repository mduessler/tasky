from __future__ import annotations

import pytest
from tests.utils import assert_paginator, parse_url
from user.models import TmsUser

BASENAME = "user"


@pytest.mark.django_db
class TestPagination:
    def test_first_page(self, superuser_read_only, users_read_only, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr("user.api.v1.paginator.TmsUserPagination.page_size", 2)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 1})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == TmsUser.objects.count()
        assert len(response.data["results"]) == 2
        assert response.data["previous"] is None
        assert response.data["next"].endswith("/?page=2")

    def test_n_page(self, superuser_read_only, users_read_only, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr("user.api.v1.paginator.TmsUserPagination.page_size", 2)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 3})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == TmsUser.objects.count()
        assert len(response.data["results"]) == 2
        assert response.data["previous"].endswith("/?page=2")
        assert response.data["next"].endswith("/?page=4")

    def test_last_page(self, superuser_read_only, users_read_only, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr("user.api.v1.paginator.TmsUserPagination.page_size", 2)
        cnt = TmsUser.objects.count()
        page = int(cnt / 2) + 1 if cnt % 2 == 1 else int(cnt / 2)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": page})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == TmsUser.objects.count()
        assert len(response.data["results"]) == 2 if cnt % 2 == 0 else 1
        assert response.data["previous"].endswith(f"/?page={page-1}")
        assert response.data["next"] is None

    def test_tasks_pagination(
        self, superuser_read_only, active_user_read_only, tasks, api_client, monkeypatch
    ):
        url = parse_url(BASENAME, "tasks", active_user_read_only.id)

        monkeypatch.setattr("task.api.v1.paginator.TaskPagination.page_size", 2)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 1})

        assert response.status_code == 200
        assert_paginator(response.data)

    def test_task_memberships_pagination(
        self, superuser_read_only, active_user_read_only, task_memberships, api_client, monkeypatch
    ):
        url = parse_url(BASENAME, "task-memberships", active_user_read_only.id)

        monkeypatch.setattr("task.api.v1.paginator.TaskMembershipPagination.page_size", 2)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 1})

        assert response.status_code == 200
        assert_paginator(response.data)

    def test_task_notes_pagination(
        self, superuser_read_only, active_user_read_only, task_notes, api_client, monkeypatch
    ):
        url = parse_url(BASENAME, "task-notes", active_user_read_only.id)

        monkeypatch.setattr("task.api.v1.paginator.TaskNotePagination.page_size", 2)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 1})

        assert response.status_code == 200
        assert_paginator(response.data)
