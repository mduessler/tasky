from unittest.mock import MagicMock

import pytest
from registration.api.v1.serializers import RegisterWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestServiceHandover:
    def test_save_handoff_to_service(self, register_data, monkeypatch):
        mock_create = MagicMock(return_value=MagicMock())
        monkeypatch.setattr("registration.services.RegistrationService.register_user", mock_create)

        serializer = RegisterWriteSerializer(
            data=register_data, context={"request": build_request("post", None)}
        )

        assert serializer.is_valid() is True

        serializer.save()

        serializer.validated_data.pop("email_verification")
        serializer.validated_data.pop("password_verification")
        mock_create.assert_called_once_with(serializer.validated_data)
