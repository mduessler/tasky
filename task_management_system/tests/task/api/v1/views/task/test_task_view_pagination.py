from __future__ import annotations

import pytest
from django.urls import reverse
from task.models import Task, TaskMembership, TaskNote
from tests.utils import assert_paginator, parse_url

BASENAME = "task"


@pytest.mark.django_db
class TestPagination:
    def test_first_page(self, superuser_read_only, tasks_read_only, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr("task.api.v1.paginator.TaskPagination.page_size", 1)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 1})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == Task.objects.count()
        assert len(response.data["results"]) == 1
        assert response.data["previous"] is None
        assert response.data["next"].endswith("/?page=2")

    def test_n_page(self, superuser_read_only, tasks_read_only, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr("task.api.v1.paginator.TaskPagination.page_size", 1)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 4})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == Task.objects.count()
        assert response.data["previous"].endswith("/?page=3")
        assert response.data["next"].endswith("/?page=5")

    def test_last_page(self, superuser_read_only, tasks_read_only, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr("task.api.v1.paginator.TaskPagination.page_size", 1)
        cnt = Task.objects.count()

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": cnt})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == cnt
        assert len(response.data["results"]) == 1
        assert response.data["previous"].endswith(f"/?page={cnt-1}")
        assert response.data["next"] is None

    def test_memberships_first_page(
        self,
        superuser_read_only,
        task_memberships_read_only,
        task_read_only,
        api_client,
        monkeypatch,
    ):
        url = reverse(f"{BASENAME}-memberships", args=[task_read_only.id])

        monkeypatch.setattr("task.api.v1.paginator.TaskMembershipPagination.page_size", 1)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 1})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert (
            response.data["count"] == TaskMembership.objects.filter(task=task_read_only.id).count()
        )
        assert len(response.data["results"]) == 1
        assert response.data["previous"] is None
        assert response.data["next"].endswith("/?page=2")

    def test_memberships_n_page(
        self,
        superuser_read_only,
        task_memberships_read_only,
        task_read_only,
        api_client,
        monkeypatch,
    ):
        url = reverse(f"{BASENAME}-memberships", args=[task_read_only.id])
        monkeypatch.setattr("task.api.v1.paginator.TaskMembershipPagination.page_size", 1)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 3})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert (
            response.data["count"] == TaskMembership.objects.filter(task=task_read_only.id).count()
        )
        assert len(response.data["results"]) == 1
        assert response.data["previous"].endswith("/?page=2")
        assert response.data["next"].endswith("/?page=4")

    def test_memberships_last_page(
        self,
        superuser_read_only,
        task_memberships_read_only,
        task_read_only,
        api_client,
        monkeypatch,
    ):
        url = reverse(f"{BASENAME}-memberships", args=[task_read_only.id])

        monkeypatch.setattr("task.api.v1.paginator.TaskMembershipPagination.page_size", 1)
        cnt = TaskMembership.objects.filter(task=task_read_only.id).count()

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": cnt})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert (
            response.data["count"] == TaskMembership.objects.filter(task=task_read_only.id).count()
        )
        assert len(response.data["results"]) == 1
        assert response.data["previous"].endswith(f"/?page={cnt-1}")
        assert response.data["next"] is None

    def test_notes_first_page(
        self, superuser_read_only, task_notes_read_only, task_read_only, api_client, monkeypatch
    ):
        url = reverse(f"{BASENAME}-notes", args=[task_read_only.id])

        monkeypatch.setattr("task.api.v1.paginator.TaskNotePagination.page_size", 1)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 1})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == TaskNote.objects.filter(task=task_read_only.id).count()
        assert len(response.data["results"]) == 1
        assert response.data["previous"] is None
        assert response.data["next"].endswith("/?page=2")

    def test_notes_n_page(
        self, superuser_read_only, task_notes_read_only, task_read_only, api_client, monkeypatch
    ):
        url = reverse(f"{BASENAME}-notes", args=[task_read_only.id])

        monkeypatch.setattr("task.api.v1.paginator.TaskNotePagination.page_size", 1)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 3})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == TaskNote.objects.filter(task=task_read_only.id).count()
        assert len(response.data["results"]) == 1
        assert response.data["previous"].endswith("/?page=2")
        assert response.data["next"].endswith("/?page=4")

    def test_notes_last_page(
        self, superuser_read_only, task_notes_read_only, task_read_only, api_client, monkeypatch
    ):
        url = reverse(f"{BASENAME}-notes", args=[task_read_only.id])

        monkeypatch.setattr("task.api.v1.paginator.TaskNotePagination.page_size", 1)
        cnt = TaskNote.objects.filter(task=task_read_only.id).count()

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": cnt})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == TaskNote.objects.filter(task=task_read_only.id).count()
        assert len(response.data["results"]) == 1
        assert response.data["previous"].endswith(f"/?page={cnt-1}")
        assert response.data["next"] is None
