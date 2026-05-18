from unittest.mock import MagicMock

import pytest
from registration.api.v1.serializers import ActivateWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestServiceHandover:
    def test_save_handoff_to_service(self, email_token, monkeypatch):
        data = {"email": email_token.user.email, "token": email_token.token}
        user = email_token.user

        mock_create = MagicMock(return_value=MagicMock())
        monkeypatch.setattr("registration.services.RegistrationService.activate_user", mock_create)

        serializer = ActivateWriteSerializer(
            data=data, context={"request": build_request("post", None)}
        )

        assert serializer.is_valid() is True

        serializer.save()
        user.refresh_from_db()

        mock_create.assert_called_once_with(**serializer.validated_data)
