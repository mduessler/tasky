import pytest
from tests.utils import build_request
from user.api.v1.serializers import TmsUserWriteSerializer


@pytest.mark.django_db
class TestValidation:
    def test_email_wrong(self, active_user, inactive_user_data):
        inactive_user_data["email"] = "   "
        serializer = TmsUserWriteSerializer(
            data=inactive_user_data, context={"request": build_request("post", active_user)}
        )

        assert serializer.is_valid() is False
        assert "email" in serializer.errors

    def test_invalid_status(self, active_user, inactive_user_data):
        inactive_user_data["username"] = ""

        serializer = TmsUserWriteSerializer(
            data=inactive_user_data, context={"request": build_request("post", active_user)}
        )

        assert serializer.is_valid() is False
        assert "username" in serializer.errors
