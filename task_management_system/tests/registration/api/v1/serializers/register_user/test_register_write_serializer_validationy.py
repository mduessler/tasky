import pytest
from registration.api.v1.serializers import RegisterWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestValidation:
    def test_validates_input_correctly(self, register_data):
        serializer = RegisterWriteSerializer(
            data=register_data, context={"request": build_request("post", None)}
        )

        assert serializer.is_valid() is True
        assert serializer.validated_data["email"] == register_data["email"]
        assert (
            serializer.validated_data["email_verification"] == register_data["email_verification"]
        )
        assert serializer.validated_data["username"] == register_data["username"]
        assert serializer.validated_data["password"] == register_data["password"]
        assert (
            serializer.validated_data["password_verification"]
            == register_data["password_verification"]
        )
        assert serializer.validated_data["first_name"] == register_data["first_name"]
        assert serializer.validated_data["last_name"] == register_data["last_name"]

    def test_email_validation_mismatch(self, register_data):
        register_data["email_verification"] = "wrong@example.com"

        serializer = RegisterWriteSerializer(data=register_data)

        assert not serializer.is_valid()
        assert serializer.errors["email_verification"][0] == "Emails do not match."

    def test_password_validation_mismatch(self, register_data):
        register_data["password_verification"] = "wrongpass123"

        serializer = RegisterWriteSerializer(data=register_data)

        assert not serializer.is_valid()
        assert serializer.errors["password_verification"][0] == "Passwords do not match."
