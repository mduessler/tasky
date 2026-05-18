from __future__ import annotations

import pytest
from django.urls import reverse

BASENAME = "activate-user"


@pytest.mark.django_db
class TestSerializerHandover:
    def test_serializer_handover(self, mocker, inactive_user, email_token, api_client):
        data = {"email": email_token.user.email, "token": email_token.token}

        url = reverse(BASENAME)

        write_serializer = mocker.Mock()
        write_serializer.is_valid.return_value = None
        write_serializer.save.return_value = inactive_user

        read_serializer = mocker.Mock()
        read_serializer.data = {
            "id": inactive_user.id,
            "email": inactive_user.email,
        }

        write_serializer_class = mocker.patch(
            "registration.api.v1.views.activate_user_view.ActivateWriteSerializer",
            return_value=write_serializer,
        )

        read_serializer_class = mocker.patch(
            "registration.api.v1.views.activate_user_view.ActivateReadSerializer",
            return_value=read_serializer,
        )

        response = api_client.post(url, data=data)

        assert response.status_code == 202
        assert response.data["id"] == inactive_user.id
        assert response.data["email"] == inactive_user.email

        write_serializer_class.assert_called_once()
        write_serializer.is_valid.assert_called_once_with(raise_exception=True)
        write_serializer.save.assert_called_once()

        _, kwargs = write_serializer_class.call_args

        assert kwargs["data"]["email"] == data["email"]
        assert kwargs["data"]["token"] == data["token"]
        assert "request" in kwargs["context"]

        read_serializer_class.assert_called_once_with(inactive_user, context=mocker.ANY)
