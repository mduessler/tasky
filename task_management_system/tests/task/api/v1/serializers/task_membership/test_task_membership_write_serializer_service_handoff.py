from unittest.mock import MagicMock

import pytest
from task.api.v1.serializers import TaskMembershipWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestServiceHandoff:
    def test_create_handoff_to_service(self, active_user, task, inactive_user, monkeypatch):
        data = {"role": "member", "user_id": inactive_user.id, "task": task.id}

        mock_create = MagicMock(return_value=MagicMock())
        monkeypatch.setattr(
            "task.services.TaskMembershipService.create",
            mock_create,
        )

        serializer = TaskMembershipWriteSerializer(
            data=data,
            context={"request": build_request("post", active_user)},
        )

        assert serializer.is_valid() is True

        serializer.save()
        mock_create.assert_called_once_with(
            active_user,
            serializer.validated_data,
        )

        assert serializer.validated_data["user"] == inactive_user

    def test_update_handoff_to_service(self, active_user, task_membership, monkeypatch):
        data = {"role": "admin"}

        mock_update = MagicMock(return_value=task_membership)
        monkeypatch.setattr(
            "task.services.TaskMembershipService.update",
            mock_update,
        )

        serializer = TaskMembershipWriteSerializer(
            instance=task_membership,
            data=data,
            partial=True,
            context={"request": build_request("patch", active_user)},
        )

        assert serializer.is_valid() is True

        serializer.save()
        mock_update.assert_called_once_with(
            active_user,
            task_membership.id,
            serializer.validated_data,
        )
