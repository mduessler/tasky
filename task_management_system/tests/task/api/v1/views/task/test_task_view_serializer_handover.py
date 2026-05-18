from __future__ import annotations

import pytest
from django.urls import reverse
from task.api.v1.serializers import TaskMembershipWriteSerializer, TaskNoteWriteSerializer
from tests.utils import parse_url

BASENAME = "task"


@pytest.mark.django_db
class TestSerializerHandover:
    def test_update_serializer_handover(self, mocker, superuser, task, api_client):
        url = parse_url(BASENAME, "detail", task.id)
        data = {"title": "Updated title"}

        write_serializer = mocker.Mock()
        write_serializer.is_valid.return_value = None
        write_serializer.save.return_value = task

        read_serializer = mocker.Mock()
        read_serializer.data = {"id": task.id, "title": data["title"]}

        write_serializer_class = mocker.patch(
            "task.api.v1.views.task.task_view.TaskWriteSerializer",
            return_value=write_serializer,
        )

        read_serializer_class = mocker.patch(
            "task.api.v1.views.task.task_view.TaskReadSerializer",
            return_value=read_serializer,
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.patch(url, data=data)

        assert response.status_code == 200
        assert response.data["id"] == task.id

        write_serializer_class.assert_called_once()
        write_serializer.is_valid.assert_called_once_with(raise_exception=True)
        write_serializer.save.assert_called_once()

        read_serializer_class.assert_called_once()
        read_serializer_class.assert_called_once_with(
            instance=task, partial=True, context=mocker.ANY
        )

    def test_create_serializer_handover(self, mocker, superuser, task, api_client):
        url = parse_url(BASENAME, "list")
        data = {"title": "Task", "description": "Description", "status": "todo"}

        write_serializer = mocker.Mock()
        write_serializer.is_valid.return_value = None
        write_serializer.save.return_value = task

        read_serializer = mocker.Mock()
        read_serializer.data = {"id": task.id}

        write_serializer_class = mocker.patch(
            "task.api.v1.views.task.task_view.TaskWriteSerializer",
            return_value=write_serializer,
        )

        read_serializer_class = mocker.patch(
            "task.api.v1.views.task.task_view.TaskReadSerializer",
            return_value=read_serializer,
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.post(url, data=data)

        assert response.status_code == 201

        write_serializer_class.assert_called_once()
        write_serializer.is_valid.assert_called_once_with(raise_exception=True)
        write_serializer.save.assert_called_once()

        read_serializer_class.assert_called_once()

    def test_membership_serializer_handover(
        self, mocker, superuser, task, user_is_not_member, task_membership, api_client
    ):
        user, _ = user_is_not_member
        url = reverse(f"{BASENAME}-membership", args=[task.id])
        data = {"user_id": user.id, "role": "viewer"}

        write_serializer = mocker.Mock(spec=TaskMembershipWriteSerializer)
        write_serializer.is_valid.return_value = None
        write_serializer.save.return_value = task_membership

        read_serializer = mocker.Mock()
        read_serializer.data = {
            "id": task_membership.id,
            "user": task_membership.user_id,
            "task": task_membership.task_id,
            "role": task_membership.role,
        }

        write_serializer_class = mocker.patch(
            "task.api.v1.views.task.task_view.TaskMembershipWriteSerializer",
            return_value=write_serializer,
        )

        read_serializer_class = mocker.patch(
            "task.api.v1.views.task.task_view.TaskMembershipReadSerializer",
            return_value=read_serializer,
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.post(url, data=data)

        assert response.status_code == 201

        write_serializer_class.assert_called_once()
        write_serializer.is_valid.assert_called_once_with(raise_exception=True)
        write_serializer.save.assert_called_once()

        read_serializer_class.assert_called_once()

    def test_note_serializer_handover(self, mocker, superuser, task, task_note, api_client):
        url = reverse(f"{BASENAME}-note", args=[task.id])
        data = {"author_id": task_note.author_id, "note": "An important note."}

        write_serializer = mocker.Mock(spec=TaskNoteWriteSerializer)
        write_serializer.is_valid.return_value = None
        write_serializer.save.return_value = task_note

        read_serializer = mocker.Mock()
        read_serializer.data = {
            "id": task_note.id,
            "author": task_note.author_id,
            "task": task_note.task_id,
            "note": "An important note.",
        }

        write_serializer_class = mocker.patch(
            "task.api.v1.views.task.task_view.TaskNoteWriteSerializer",
            return_value=write_serializer,
        )

        read_serializer_class = mocker.patch(
            "task.api.v1.views.task.task_view.TaskNoteReadSerializer",
            return_value=read_serializer,
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.post(url, data=data)

        assert response.status_code == 201

        write_serializer_class.assert_called_once()
        write_serializer.is_valid.assert_called_once_with(raise_exception=True)
        write_serializer.save.assert_called_once()

        read_serializer_class.assert_called_once()

    def test_query_serializer_handover(self, mocker, superuser, api_client):
        url = parse_url(BASENAME, "list")

        serializer = mocker.Mock()
        serializer.is_valid.return_value = None
        serializer.validated_data = {"user": superuser, "status": None}

        serializer_class = mocker.patch(
            "task.api.v1.views.task.task_view.TaskQuerySerializer",
            return_value=serializer,
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)

        assert response.status_code == 200

        serializer_class.assert_called_once()
        serializer.is_valid.assert_called_once_with(raise_exception=True)
