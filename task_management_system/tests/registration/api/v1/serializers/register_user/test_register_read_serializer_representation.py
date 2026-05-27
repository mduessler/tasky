import pytest
from registration.api.v1.serializers import RegisterReadSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestReadSerializerRepresentaion:
    def test_serializes_expected_fields(self, active_user):
        serializer = RegisterReadSerializer(
            instance=active_user, context={"request": build_request("post", None)}
        )

        assert serializer.data["email"] == active_user.email
        assert serializer.data["username"] == active_user.username
        assert "id" not in serializer.data
        assert "password" not in serializer.data
