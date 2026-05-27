from __future__ import annotations

from unittest.mock import patch

import pytest
from task.models import TaskNote
from tests.utils import parse_url

BASENAME = "note"


@pytest.mark.django_db
class TestServiceHandover:
    @patch("task.services.TaskNoteService.get_task_note")
    def test_get_object(self, mock_get_note, superuser, task_note, api_client):
        url = parse_url(BASENAME, "detail", task_note.id)
        mock_get_note.return_value = task_note

        api_client.force_authenticate(user=superuser)
        api_client.get(url)

        mock_get_note.assert_called_once_with(superuser, task_note.id)

    @patch("task.services.TaskNoteService.get_task_notes")
    def test_get_queryset(self, mock_get_notes, superuser, api_client):
        url = parse_url(BASENAME, "list")
        mock_get_notes.return_value = TaskNote.objects.all()

        api_client.force_authenticate(user=superuser)
        api_client.get(url)

        mock_get_notes.assert_called_once_with(superuser)

    @patch("task.services.TaskNoteService.delete")
    def test_perform_destroy(self, delete, superuser, task_note, api_client):
        url = parse_url(BASENAME, "detail", task_note.id)
        delete.return_value = None

        api_client.force_authenticate(user=superuser)
        api_client.delete(url)

        delete.assert_called_once_with(superuser, task_note.id)
