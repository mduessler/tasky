import pytest
from task.models import Task, TaskMembership, TaskNote
from task.services import TaskService
from tests.task.api.v1.views.utils import (
    assert_task_membership_response_body,
    assert_task_note_response_body,
    assert_task_response_body,
)
from tests.utils import assert_paginator, extract_results, parse_url

BASENAME = "task"


@pytest.mark.django_db
class TestResponseBodyOK:
    def test_list(self, superuser, tasks, api_client):
        url = parse_url(BASENAME, "list")

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)

        for data in extract_results(response.data):
            task = Task.objects.get(id=data["id"])
            assert_task_response_body(data, task, superuser)

    def test_list_empty_body(self, superuser, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr(TaskService, "get_tasks", lambda a, status=None: Task.objects.none())

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
    def test_retrieve(self, actor_fixture, request, task, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)
        url = parse_url(BASENAME, "detail", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_task_response_body(response.data, task, actor)

    @pytest.mark.parametrize("actor_fixture", ["member_is_owner", "superuser_is_not_member"])
    def test_patch(self, actor_fixture, request, task, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)
        old_title = task.title

        url = parse_url(BASENAME, "detail", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.patch(url, data={"title": "updated"})

        task.refresh_from_db()

        assert response.status_code == 200
        assert task.title != old_title
        assert_task_response_body(response.data, task, actor)

    @pytest.mark.parametrize("actor_fixture", ["member_is_owner", "superuser_is_not_member"])
    def test_delete(self, actor_fixture, request, task, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)
        task_id = task.id
        url = parse_url(BASENAME, "detail", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.delete(url)

        assert response.status_code == 204
        assert Task.objects.filter(id=task_id).exists() is False

    def test_create(self, superuser, api_client):
        url = parse_url(BASENAME, "list")

        api_client.force_authenticate(user=superuser)
        response = api_client.post(
            url,
            data={
                "title": "task",
                "description": "description",
                "status": "todo",
            },
        )

        assert response.status_code == 201

        task = Task.objects.get(id=response.data["id"])

        assert_task_response_body(response.data, task, superuser)

    def test_memberships(self, superuser, task_memberships, task, api_client):
        url = parse_url(BASENAME, "memberships", task.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)

        for data in extract_results(response.data):
            membership = TaskMembership.objects.get(id=data["id"])
            assert_task_membership_response_body(data, membership, superuser)

    def test_memberships_empty_body(
        self,
        superuser,
        task,
        api_client,
        monkeypatch,
    ):
        url = parse_url(BASENAME, "memberships", task.id)

        monkeypatch.setattr(
            TaskService,
            "get_memberships_of_task",
            lambda a, t: TaskMembership.objects.none(),
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert extract_results(response.data) == []

    def test_membership_create(self, member_is_owner, task, data_task_membership, api_client):
        actor, _ = member_is_owner
        url = parse_url(BASENAME, "membership", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.post(url, data=data_task_membership)

        assert response.status_code == 201

        membership = TaskMembership.objects.get(id=response.data["id"])

        assert_task_membership_response_body(response.data, membership, actor)

    def test_notes(self, superuser, task_notes, task, api_client):
        url = parse_url(BASENAME, "notes", task.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)

        for data in extract_results(response.data):
            note = TaskNote.objects.get(id=data["id"])
            assert_task_note_response_body(data, note, superuser)

    def test_notes_empty_body(self, superuser, task, api_client, monkeypatch):
        url = parse_url(BASENAME, "notes", task.id)

        monkeypatch.setattr(TaskService, "get_notes_of_task", lambda a, t: TaskNote.objects.none())

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert extract_results(response.data) == []

    def test_note_create(self, member_is_owner, data_task_note_author_is_member, task, api_client):
        actor, _ = member_is_owner
        url = parse_url(BASENAME, "note", task.id)

        api_client.force_authenticate(user=actor)
        response = api_client.post(url, data=data_task_note_author_is_member)

        assert response.status_code == 201

        note = TaskNote.objects.get(id=response.data["id"])

        assert_task_note_response_body(response.data, note, actor)
