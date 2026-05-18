from __future__ import annotations

import pytest
from tests.utils import parse_url

BASENAME = "membership"


@pytest.mark.django_db
class TestSerializerHandover:
    def test_update_serializer_handover(self, mocker, superuser, task_membership, api_client):
        url = parse_url(BASENAME, "detail", task_membership.id)
        data = {"role": "viewer"}

        write_serializer = mocker.Mock()
        write_serializer.is_valid.return_value = None
        write_serializer.save.return_value = task_membership

        read_serializer = mocker.Mock()
        read_serializer.data = {"id": task_membership.id, "role": "viewer"}

        write_serializer_class = mocker.patch(
            "task.api.v1.views.task_membership.task_membership_view."
            "TaskMembershipWriteSerializer",
            return_value=write_serializer,
        )

        read_serializer_class = mocker.patch(
            "task.api.v1.views.task_membership.task_membership_view."
            "TaskMembershipReadSerializer",
            return_value=read_serializer,
        )

        api_client.force_authenticate(user=superuser)
        response = api_client.patch(url, data=data)

        assert response.status_code == 200
        assert response.data["id"] == task_membership.id
        assert response.data["role"] == "viewer"

        write_serializer_class.assert_called_once()
        write_serializer.is_valid.assert_called_once_with(raise_exception=True)
        write_serializer.save.assert_called_once()

        read_serializer_class.assert_called_once()
        read_serializer_class.assert_called_once_with(
            instance=task_membership,
            partial=True,
            context=mocker.ANY,
        )
