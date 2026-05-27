from __future__ import annotations

import pytest
from tests.utils import parse_url

BASENAME = "user"


@pytest.mark.django_db
class TestSerializerSelection:
    def test_tasks_serializer(self, mocker, superuser, active_user, api_client):
        url = parse_url(BASENAME, "tasks", active_user.id)

        serializer_instance = mocker.Mock()
        serializer_instance.data = []

        serializer = mocker.patch(
            "user.api.v1.views.tms_user_view.TaskReadSerializer",
            return_value=serializer_instance,
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200
        assert serializer.called is True

    def test_task_memberships_serializer(self, mocker, superuser, active_user, api_client):
        url = parse_url(BASENAME, "task-memberships", active_user.id)
        serializer_instance = mocker.Mock()
        serializer_instance.data = []

        serializer = mocker.patch(
            "user.api.v1.views.tms_user_view.TaskMembershipReadSerializer",
            return_value=serializer_instance,
        )

        api_client.force_authenticate(user=superuser)
        api_client.get(url)

        assert serializer.called is True

    def test_task_notes_serializer(self, mocker, superuser, active_user, api_client):
        url = parse_url(BASENAME, "task-notes", active_user.id)

        serializer_instance = mocker.Mock()
        serializer_instance.data = []

        serializer = mocker.patch(
            "user.api.v1.views.tms_user_view.TaskNoteReadSerializer",
            return_value=serializer_instance,
        )

        api_client.force_authenticate(user=superuser)
        api_client.get(url)

        assert serializer.called is True
