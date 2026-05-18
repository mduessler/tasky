from __future__ import annotations

import pytest
from django.urls import resolve, reverse

BASENAME = "user"


@pytest.mark.django_db
class TestUrlRoute:
    def test_list_reverse(self):
        assert "/api/v1/user/" == reverse(f"{BASENAME}-list")

    def test_list_resolve(self):
        resolver = resolve("/api/v1/user/")
        assert resolver.view_name == f"{BASENAME}-list"

    def test_detail_reverse(self):
        url = reverse(f"{BASENAME}-detail", args=[1])
        assert "/api/v1/user/1/" == url

    def test_detail_resolve(self):
        resolver = resolve("/api/v1/user/1/")
        assert resolver.view_name == f"{BASENAME}-detail"

    def test_tasks_reverse(self):
        url = reverse(f"{BASENAME}-tasks", args=[1])

        assert url == "/api/v1/user/1/tasks/"

    def test_tasks_resolve(self):
        resolver = resolve("/api/v1/user/1/tasks/")

        assert resolver.view_name == f"{BASENAME}-tasks"

    def test_task_memberships_reverse(self):
        url = reverse(f"{BASENAME}-task-memberships", args=[1])

        assert url == "/api/v1/user/1/task_memberships/"

    def test_task_memberships_resolve(self):
        resolver = resolve("/api/v1/user/1/task_memberships/")

        assert resolver.view_name == f"{BASENAME}-task-memberships"

    def test_task_notes_reverse(self):
        url = reverse(f"{BASENAME}-task-notes", args=[1])

        assert url == "/api/v1/user/1/task_notes/"

    def test_task_notes_resolve(self):
        resolver = resolve("/api/v1/user/1/task_notes/")

        assert resolver.view_name == f"{BASENAME}-task-notes"
