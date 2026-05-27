from __future__ import annotations

from unittest.mock import patch

import pytest
from task.models import Task, TaskMembership, TaskNote
from tests.utils import parse_url
from user.models import TmsUser

BASENAME = "user"


@pytest.mark.django_db
class TestServiceHandover:
    @patch("user.services.TmsUserService.get_user_via_id")
    def test_get_object(self, mock_get_user_via_id, superuser, active_user, api_client):
        url = parse_url(BASENAME, "detail", active_user.id)
        mock_get_user_via_id.return_value = active_user

        api_client.force_authenticate(user=superuser)
        api_client.get(url)

        mock_get_user_via_id.assert_called_once_with(superuser, active_user.id)

    @patch("user.services.TmsUserService.get_users")
    def test_get_queryset(self, mock_get_users, superuser, api_client):
        url = parse_url(BASENAME, "list")
        mock_get_users.return_value = TmsUser.objects.all()

        api_client.force_authenticate(user=superuser)
        api_client.get(url)

        mock_get_users.assert_called_once_with(superuser)

    @patch("user.services.TmsUserService.delete")
    def test_perform_destroy(self, delete, superuser, active_user, api_client):
        url = parse_url(BASENAME, "detail", active_user.id)
        delete.return_value = None

        api_client.force_authenticate(user=superuser)
        api_client.delete(url)

        delete.assert_called_once_with(superuser, active_user.id)

    @patch("user.services.TmsUserService.get_tasks_of_user")
    def test_get_tasks_of_user(self, mock_get_tasks_of_user, superuser, active_user, api_client):
        url = parse_url(BASENAME, "tasks", active_user.id)

        mock_get_tasks_of_user.return_value = Task.objects.none()

        api_client.force_authenticate(user=superuser)
        api_client.get(url)

        mock_get_tasks_of_user.assert_called_once_with(superuser, active_user.id)

    @patch("user.services.TmsUserService.get_memberships_of_user")
    def test_get_memberships_of_user(
        self, mock_get_memberships_of_user, superuser, active_user, api_client
    ):
        url = parse_url(BASENAME, "task-memberships", active_user.id)

        mock_get_memberships_of_user.return_value = TaskMembership.objects.none()

        api_client.force_authenticate(user=superuser)
        api_client.get(url)

        mock_get_memberships_of_user.assert_called_once_with(superuser, active_user.id)

    @patch("user.services.TmsUserService.get_notes_of_user")
    def test_get_user_notes(self, mock_get_user_notes, superuser, active_user, api_client):
        url = parse_url(BASENAME, "task-notes", active_user.id)

        mock_get_user_notes.return_value = TaskNote.objects.none()

        api_client.force_authenticate(user=superuser)
        api_client.get(url)

        mock_get_user_notes.assert_called_once_with(superuser, active_user.id)
