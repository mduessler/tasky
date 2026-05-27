from __future__ import annotations

from types import SimpleNamespace

import pytest
from django.urls import reverse

BASENAME = "register-user"


@pytest.mark.django_db
class TestSerializerHandover:
    def test_serializer_handover(self, mocker, register_data, api_client):
        fake_user = SimpleNamespace(
            id=1000,
            email="kevin@example.com",
        )

        url = reverse(BASENAME)

        write_serializer = mocker.Mock()
        write_serializer.is_valid.return_value = None
        write_serializer.save.return_value = fake_user

        read_serializer = mocker.Mock()
        read_serializer.data = {"id": fake_user.id, "email": fake_user.email}

        write_serializer_class = mocker.patch(
            "registration.api.v1.views.register_user_view.RegisterWriteSerializer",
            return_value=write_serializer,
        )

        read_serializer_class = mocker.patch(
            "registration.api.v1.views.register_user_view.RegisterReadSerializer",
            return_value=read_serializer,
        )

        response = api_client.post(url, data=register_data)

        assert response.status_code == 201
        assert response.data["id"] == fake_user.id
        assert response.data["email"] == fake_user.email

        write_serializer_class.assert_called_once()

        _, kwargs = write_serializer_class.call_args

        assert kwargs["data"]["email"] == register_data["email"]
        assert "request" in kwargs["context"]

        write_serializer.is_valid.assert_called_once_with(raise_exception=True)
        write_serializer.save.assert_called_once()

        read_serializer_class.assert_called_once_with(fake_user, context=mocker.ANY)
