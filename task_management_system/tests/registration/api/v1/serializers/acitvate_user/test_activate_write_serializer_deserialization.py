import pytest
from registration.api.v1.serializers import ActivateWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestDeseralization:
    def test_validates_input_correctly(self, email_token):
        data = {"email": email_token.user.email, "token": email_token.token}

        serializer = ActivateWriteSerializer(
            data=data, context={"request": build_request("post", None)}
        )

        assert serializer.is_valid() is True
        assert serializer.validated_data["email"] == data["email"]
        assert serializer.validated_data["token"] == data["token"]
