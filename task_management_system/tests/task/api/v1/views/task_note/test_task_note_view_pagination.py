from __future__ import annotations

import pytest
from task.models import TaskNote
from tests.utils import assert_paginator, parse_url

BASENAME = "note"


@pytest.mark.django_db
class TestPagination:
    def test_first_page(self, superuser_read_only, task_notes_read_only, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr("task.api.v1.paginator.TaskNotePagination.page_size", 1)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 1})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == TaskNote.objects.count()
        assert len(response.data["results"]) == 1
        assert response.data["previous"] is None
        assert response.data["next"].endswith("/?page=2")

    def test_n_page(self, superuser_read_only, task_notes_read_only, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr("task.api.v1.paginator.TaskNotePagination.page_size", 1)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": 3})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == TaskNote.objects.count()
        assert len(response.data["results"]) == 1
        assert response.data["previous"].endswith("/?page=2")
        assert response.data["next"].endswith("/?page=4")

    def test_last_page(self, superuser_read_only, task_notes_read_only, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr("task.api.v1.paginator.TaskNotePagination.page_size", 1)

        cnt = TaskNote.objects.count()
        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.get(url, data={"page": cnt})

        assert response.status_code == 200
        assert_paginator(response.data)
        assert response.data["count"] == TaskNote.objects.count()
        assert len(response.data["results"]) == 1
        assert response.data["previous"].endswith(f"/?page={cnt-1}")
        assert response.data["next"] is None
