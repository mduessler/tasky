from __future__ import annotations

import pytest
from tests.utils import parse_url

BASENAME = "user"


@pytest.mark.django_db
class TestSerializerHandover:
    def test_update_serializer_handover(self, mocker, superuser, active_user, api_client):
        url = parse_url(BASENAME, "detail", active_user.id)

        data = {"username": "new_username"}

        write_serializer = mocker.Mock()
        write_serializer.is_valid.return_value = None
        write_serializer.save.return_value = active_user

        read_serializer = mocker.Mock()
        read_serializer.data = {"id": active_user.id, "username": "new_username"}

        write_serializer_class = mocker.patch(
            "user.api.v1.views.tms_user_view.TmsUserWriteSerializer",
            return_value=write_serializer,
        )

        read_serializer_class = mocker.patch(
            "user.api.v1.views.tms_user_view.TmsUserReadSerializer",
            return_value=read_serializer,
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.patch(url, data=data)

        assert response.status_code == 200
        assert response.data["id"] == active_user.id
        assert response.data["username"] == "new_username"

        write_serializer_class.assert_called_once()
        write_serializer.is_valid.assert_called_once_with(raise_exception=True)
        write_serializer.save.assert_called_once()

        read_serializer_class.assert_called_once()
        read_serializer_class.assert_called_once_with(
            active_user, partial=True, context=mocker.ANY
        )

    def test_tasks_serializer_handover(self, mocker, superuser, active_user, api_client):
        url = parse_url(BASENAME, "tasks", active_user.id)

        serializer = mocker.Mock()
        serializer.data = []

        serializer_class = mocker.patch(
            "user.api.v1.views.tms_user_view.TaskReadSerializer",
            return_value=serializer,
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200

        serializer_class.assert_called()
        _, kwargs = serializer_class.call_args

        assert kwargs["many"] is True

    def test_task_memberships_serializer_handover(
        self, mocker, superuser, active_user, api_client
    ):
        url = parse_url(BASENAME, "task-memberships", active_user.id)

        serializer = mocker.Mock()
        serializer.data = []

        serializer_class = mocker.patch(
            "user.api.v1.views.tms_user_view.TaskMembershipReadSerializer",
            return_value=serializer,
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200

        serializer_class.assert_called()
        _, kwargs = serializer_class.call_args

        assert kwargs["many"] is True

    def test_task_notes_serializer_handover(self, mocker, superuser, active_user, api_client):
        url = parse_url(BASENAME, "task-notes", active_user.id)

        serializer = mocker.Mock()
        serializer.data = []

        serializer_class = mocker.patch(
            "user.api.v1.views.tms_user_view.TaskNoteReadSerializer",
            return_value=serializer,
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200

        serializer_class.assert_called()
        _, kwargs = serializer_class.call_args

        assert kwargs["many"] is True
