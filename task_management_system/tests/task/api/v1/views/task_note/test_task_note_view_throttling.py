from __future__ import annotations

import pytest
from task.api.v1.serializers import TaskNoteWriteSerializer
from task.api.v1.throttling import (
    TaskNoteDeleteBurst,
    TaskNoteDeleteSustained,
    TaskNoteReadBurst,
    TaskNoteReadSustained,
    TaskNoteUpdateBurst,
    TaskNoteUpdateSustained,
)
from task.services import TaskNoteService
from tests.utils import assert_burst_throttle, assert_sustained_throttle, parse_url

BASENAME = "note"


@pytest.mark.django_db
class TestThrottling:
    def test_read_burst_throttle(self, superuser_read_only, api_client):
        assert_burst_throttle(
            superuser_read_only,
            parse_url(BASENAME, "list"),
            "get",
            api_client,
            "task_note_read",
            2,
            100,
            TaskNoteReadBurst,
            TaskNoteReadSustained,
        )

    def test_read_sustained_throttle(self, superuser_read_only, api_client):
        assert_sustained_throttle(
            superuser_read_only,
            parse_url(BASENAME, "list"),
            "get",
            api_client,
            "task_note_read",
            100,
            2,
            TaskNoteReadBurst,
            TaskNoteReadSustained,
        )

    def test_delete_burst_throttle(
        self, superuser_read_only, task_note_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(TaskNoteService, "delete", lambda a, n: None)

        assert_burst_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_note_read_only.id),
            "delete",
            api_client,
            "task_note_delete",
            2,
            100,
            TaskNoteDeleteBurst,
            TaskNoteDeleteSustained,
        )

    def test_delete_sustained_throttle(
        self, superuser_read_only, task_note_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(TaskNoteService, "delete", lambda a, n: None)

        assert_sustained_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_note_read_only.id),
            "delete",
            api_client,
            "task_note_delete",
            100,
            2,
            TaskNoteDeleteBurst,
            TaskNoteDeleteSustained,
        )

    def test_update_burst_throttle(
        self, superuser_read_only, task_note_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(TaskNoteWriteSerializer, "save", lambda s: task_note_read_only)

        assert_burst_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_note_read_only.id),
            "patch",
            api_client,
            "task_note_update",
            2,
            100,
            TaskNoteUpdateBurst,
            TaskNoteUpdateSustained,
        )

    def test_update_sustained_throttle(
        self, superuser_read_only, task_note_read_only, api_client, monkeypatch
    ):
        monkeypatch.setattr(TaskNoteWriteSerializer, "save", lambda s: task_note_read_only)

        assert_sustained_throttle(
            superuser_read_only,
            parse_url(BASENAME, "detail", task_note_read_only.id),
            "patch",
            api_client,
            "task_note_update",
            100,
            2,
            TaskNoteUpdateBurst,
            TaskNoteUpdateSustained,
        )
