from __future__ import annotations

from unittest.mock import patch

import pytest
from task.models import TaskMembership
from tests.utils import parse_url

BASENAME = "membership"


@pytest.mark.django_db
class TestServiceHandover:
    @patch("task.services.TaskMembershipService.get_task_membership")
    def test_get_object(self, mock_get_membership, superuser, task_membership, api_client):
        url = parse_url(BASENAME, "detail", task_membership.id)
        mock_get_membership.return_value = task_membership

        api_client.force_authenticate(user=superuser)
        api_client.get(url)

        mock_get_membership.assert_called_once_with(superuser, task_membership.id)

    @patch("task.services.TaskMembershipService.get_task_memberships")
    def test_get_queryset(self, mock_get_memberships, superuser, api_client):
        url = parse_url(BASENAME, "list")
        mock_get_memberships.return_value = TaskMembership.objects.all()

        api_client.force_authenticate(user=superuser)
        api_client.get(url)

        mock_get_memberships.assert_called_once_with(superuser)

    @patch("task.services.TaskMembershipService.delete")
    def test_perform_destroy(self, delete, superuser, task_membership, api_client):
        url = parse_url(BASENAME, "detail", task_membership.id)
        delete.return_value = None

        api_client.force_authenticate(user=superuser)
        api_client.delete(url)

        delete.assert_called_once_with(superuser, task_membership.id)
