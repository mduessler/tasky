from __future__ import annotations

import pytest
from task.models import TaskNote
from task.services import TaskNoteService
from tests.task.api.v1.views.utils import assert_task_note_response_body
from tests.utils import assert_paginator, extract_results, parse_url

BASENAME = "note"


@pytest.mark.django_db
class TestResponseBodyOK:
    def test_list(self, superuser, task_notes, api_client):
        url = parse_url(BASENAME, "list")

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_paginator(response.data)

        for data in extract_results(response.data):
            note = TaskNote.objects.get(id=data["id"])
            assert_task_note_response_body(data, note, superuser)

    def test_list_empty_body(self, superuser, api_client, monkeypatch):
        url = parse_url(BASENAME, "list")

        monkeypatch.setattr(TaskNoteService, "get_task_notes", lambda s: TaskNote.objects.none())

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
    def test_retrieve(self, actor_fixture, request, task_note, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)
        url = parse_url(BASENAME, "detail", task_note.id)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 200
        assert_task_note_response_body(response.data, task_note, actor)

    @pytest.mark.parametrize(
        "actor_fixture", ["member_is_owner", "member_is_admin", "superuser_is_not_member"]
    )
    def test_patch(self, actor_fixture, request, task_note, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)
        old_note = task_note.note
        data = {"note": "updated note"}
        url = parse_url(BASENAME, "detail", task_note.id)

        api_client.force_authenticate(user=actor)
        response = api_client.patch(url, data=data)

        task_note.refresh_from_db()

        assert response.status_code == 200
        assert task_note.note != old_note
        assert_task_note_response_body(response.data, task_note, actor)

    @pytest.mark.parametrize(
        "actor_fixture", ["member_is_owner", "member_is_admin", "superuser_is_not_member"]
    )
    def test_delete(self, actor_fixture, request, task_note, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)
        note_id = task_note.id
        url = parse_url(BASENAME, "detail", task_note.id)

        api_client.force_authenticate(user=actor)
        response = api_client.delete(url)

        assert response.status_code == 204
        assert TaskNote.objects.filter(id=note_id).exists() is False
