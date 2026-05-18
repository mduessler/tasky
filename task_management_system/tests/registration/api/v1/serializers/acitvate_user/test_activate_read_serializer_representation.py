import pytest
from registration.api.v1.serializers import ActivateReadSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestReadSerializerRepresentaion:
    def test_serializes_expected_fields(self, inactive_user):
        serializer = ActivateReadSerializer(
            instance=inactive_user, context={"request": build_request("post", None)}
        )

        assert serializer.data["id"] == inactive_user.id
        assert serializer.data["email"] == inactive_user.email
        assert serializer.data["username"] == inactive_user.username
        assert "password" not in serializer.data
