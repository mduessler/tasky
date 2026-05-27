from __future__ import annotations

from unittest.mock import patch

import pytest
from django.urls import reverse
from task.models import Task, TaskMembership, TaskNote
from tests.utils import parse_url

BASENAME = "task"


@pytest.mark.django_db
class TestServiceHandover:
    @patch("task.services.TaskService.get_task")
    def test_get_object(self, mock_get_task, superuser, task, api_client):
        url = parse_url(BASENAME, "detail", task.id)
        mock_get_task.return_value = task

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        mock_get_task.assert_called_once_with(superuser, task.id)

    @patch("task.services.TaskService.get_tasks")
    def test_get_queryset(self, mock_get_tasks, superuser, api_client):
        url = parse_url(BASENAME, "list")
        mock_get_tasks.return_value = Task.objects.all()

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        mock_get_tasks.assert_called_once()
        mock_get_tasks.assert_called_once_with(superuser, None)

    @patch("task.services.TaskService.delete")
    def test_perform_destroy(self, mock_delete, superuser, task, api_client):
        url = parse_url(BASENAME, "detail", task.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.delete(url)

        assert response.status_code == 204
        mock_delete.assert_called_once_with(superuser, task.id)

    @patch("task.services.TaskService.get_memberships_of_task")
    def test_memberships_service_handover(self, mock_get_memberships, superuser, task, api_client):
        url = reverse(f"{BASENAME}-memberships", args=[task.id])
        mock_get_memberships.return_value = TaskMembership.objects.all()

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        mock_get_memberships.assert_called_once_with(superuser, task)

    @patch("task.services.TaskService.get_notes_of_task")
    def test_notes_service_handover(self, mock_get_notes, superuser, task, api_client):
        url = reverse(f"{BASENAME}-notes", args=[task.id])
        mock_get_notes.return_value = TaskNote.objects.all()

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        mock_get_notes.assert_called_once_with(superuser, task)
