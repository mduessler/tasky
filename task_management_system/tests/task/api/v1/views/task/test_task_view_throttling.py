from __future__ import annotations

import pytest
from django.urls import reverse
from task.api.v1.serializers import (
    TaskMembershipWriteSerializer,
    TaskNoteWriteSerializer,
    TaskWriteSerializer,
)
from task.api.v1.throttling import (
    TaskCreateBurst,
    TaskCreateSustained,
    TaskDeleteBurst,
    TaskDeleteSustained,
    TaskMembershipCreateBurst,
    TaskMembershipCreateSustained,
    TaskMembershipReadBurst,
    TaskMembershipReadSustained,
    TaskNoteCreateBurst,
    TaskNoteCreateSustained,
    TaskNoteReadBurst,
    TaskNoteReadSustained,
    TaskReadBurst,
    TaskReadSustained,
    TaskUpdateBurst,
    TaskUpdateSustained,
)
from task.services import TaskService
from tests.utils import assert_burst_throttle, assert_sustained_throttle, parse_url

BASENAME = "task"


@pytest.mark.django_db
class TestThrottling:
    def test_read_burst_throttle(self, superuser_read_only, api_client):
        assert_burst_throttle(
            superuser_read_only,
            parse_url(BASENAME, "list"),
            "get",
            api_client,
            "task_read",
            2,
            100,
            TaskReadBurst,
            TaskReadSustained,
        )

    def test_read_sustained_throttle(self, superuser_read_only, api_client):
        assert_sustained_throttle(
            superuser_read_only,
            parse_url(BASENAME, "list"),
            "get",
            api_client,
            "task_read",
            100,
            2,
            TaskReadBurst,
            TaskReadSustained,
        )

    def test_create_burst_throttle(
        self, superuser_read_only, api_client, monkeypatch, task_read_only
    ):
        monkeypatch.setattr(
            TaskWriteSerializer,
            "save",
            lambda s: task_read_only,
        )

        assert_burst_throttle(
            superuser_read_only,
            parse_url(BASENAME, "list"),
            "post",
            api_client,
            "task_create",
            2,
            100,
            TaskCreateBurst,
            TaskCreateSustained,
            data={
                "title": "Task",
                "description": "Description",
                "status": "todo",
            },
        )

    def test_create_sustained_throttle(
        self, superuser_read_only, api_client, monkeypatch, task_read_only
    ):
        monkeypatch.setattr(
            TaskWriteSerializer,
            "save",
            lambda s: task_read_only,
        )

        assert_sustained_throttle(
            superuser_read_only,
            parse_url(BASENAME, "list"),
            "post",
            api_client,
            "task_create",
            100,
            2,
            TaskCreateBurst,
            TaskCreateSustained,
            data={
                "title": "Task",
                "description": "Description",
                "status": "todo",
            },
        )

    def test_update_burst_throttle(
        self, superuser_read_only, task_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(
            TaskWriteSerializer,
            "save",
            lambda s: task_read_only,
        )

        assert_burst_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_read_only.id),
            "patch",
            api_client,
            "task_update",
            2,
            100,
            TaskUpdateBurst,
            TaskUpdateSustained,
            data={"title": "Updated"},
        )

    def test_update_sustained_throttle(
        self, superuser_read_only, task_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(TaskWriteSerializer, "save", lambda s: task_read_only)

        assert_sustained_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_read_only.id),
            "patch",
            api_client,
            "task_update",
            100,
            2,
            TaskUpdateBurst,
            TaskUpdateSustained,
            data={"title": "Updated"},
        )

    def test_delete_burst_throttle(
        self, superuser_read_only, task_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(TaskService, "delete", lambda a, t: None)

        assert_burst_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_read_only.id),
            "delete",
            api_client,
            "task_delete",
            2,
            100,
            TaskDeleteBurst,
            TaskDeleteSustained,
        )

    def test_delete_sustained_throttle(
        self, superuser_read_only, task_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(TaskService, "delete", lambda a, t: None)

        assert_sustained_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_read_only.id),
            "delete",
            api_client,
            "task_delete",
            100,
            2,
            TaskDeleteBurst,
            TaskDeleteSustained,
        )

    def test_membership_create_burst_throttle(
        self,
        superuser_read_only,
        task_read_only,
        user_is_not_member_read_only,
        task_membership_read_only,
        api_client,
        monkeypatch,
    ):
        monkeypatch.setattr(
            TaskMembershipWriteSerializer, "save", lambda s: task_membership_read_only
        )
        user, _ = user_is_not_member_read_only

        assert_burst_throttle(
            superuser_read_only,
            reverse(f"{BASENAME}-membership", kwargs={"pk": task_read_only.id}),
            "post",
            api_client,
            "task_membership_create",
            2,
            100,
            TaskMembershipCreateBurst,
            TaskMembershipCreateSustained,
            data={"user_id": user.id, "role": "viewer"},
        )

    def test_membership_create_sustained_throttle(
        self,
        superuser_read_only,
        task_read_only,
        user_is_not_member_read_only,
        task_membership_read_only,
        api_client,
        monkeypatch,
    ):
        monkeypatch.setattr(
            TaskMembershipWriteSerializer, "save", lambda s: task_membership_read_only
        )
        user, _ = user_is_not_member_read_only

        assert_sustained_throttle(
            superuser_read_only,
            reverse(f"{BASENAME}-membership", kwargs={"pk": task_read_only.id}),
            "post",
            api_client,
            "task_membership_create",
            100,
            2,
            TaskMembershipCreateBurst,
            TaskMembershipCreateSustained,
            data={"user_id": user.id, "role": "viewer"},
        )

    def test_memberships_read_burst_throttle(
        self, superuser_read_only, task_read_only, api_client
    ):
        assert_burst_throttle(
            superuser_read_only,
            reverse(f"{BASENAME}-memberships", kwargs={"pk": task_read_only.id}),
            "get",
            api_client,
            "task_membership_read",
            2,
            100,
            TaskMembershipReadBurst,
            TaskMembershipReadSustained,
        )

    def test_memberships_read_sustained_throttle(
        self, superuser_read_only, task_read_only, api_client
    ):
        assert_sustained_throttle(
            superuser_read_only,
            reverse(f"{BASENAME}-memberships", kwargs={"pk": task_read_only.id}),
            "get",
            api_client,
            "task_membership_read",
            100,
            2,
            TaskMembershipReadBurst,
            TaskMembershipReadSustained,
        )

    def test_note_create_burst_throttle(
        self, superuser_read_only, task_read_only, task_note_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(TaskNoteWriteSerializer, "save", lambda s: task_note_read_only)

        assert_burst_throttle(
            superuser_read_only,
            reverse(f"{BASENAME}-note", kwargs={"pk": task_read_only.id}),
            "post",
            api_client,
            "task_note_create",
            2,
            100,
            TaskNoteCreateBurst,
            TaskNoteCreateSustained,
            data={"author_id": task_note_read_only.author_id, "note": "A very important note."},
        )

    def test_note_create_sustained_throttle(
        self, superuser_read_only, task_read_only, task_note_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(TaskNoteWriteSerializer, "save", lambda s: task_note_read_only)

        assert_sustained_throttle(
            superuser_read_only,
            reverse(f"{BASENAME}-note", kwargs={"pk": task_read_only.id}),
            "post",
            api_client,
            "task_note_create",
            100,
            2,
            TaskNoteCreateBurst,
            TaskNoteCreateSustained,
            data={"author_id": task_note_read_only.author_id, "note": "A very important note."},
        )

    def test_notes_read_burst_throttle(self, superuser_read_only, task_read_only, api_client):
        assert_burst_throttle(
            superuser_read_only,
            reverse(f"{BASENAME}-notes", kwargs={"pk": task_read_only.id}),
            "get",
            api_client,
            "task_note_read",
            2,
            100,
            TaskNoteReadBurst,
            TaskNoteReadSustained,
        )

    def test_notes_read_sustained_throttle(self, superuser_read_only, task_read_only, api_client):
        assert_sustained_throttle(
            superuser_read_only,
            reverse(f"{BASENAME}-notes", kwargs={"pk": task_read_only.id}),
            "get",
            api_client,
            "task_note_read",
            100,
            2,
            TaskNoteReadBurst,
            TaskNoteReadSustained,
        )
