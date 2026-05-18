import pytest
from tests.utils import build_request
from user.api.v1.serializers import TmsUserWriteSerializer


@pytest.mark.django_db
class TestDeserialization:
    def test_validates_input_correctly(self, superuser, inactive_user, inactive_user_data):
        inactive_user_data["is_staff"] = False
        inactive_user_data["is_superuser"] = False
        inactive_user_data["is_active"] = False

        serializer = TmsUserWriteSerializer(
            instance=inactive_user,
            data=inactive_user_data,
            context={"request": build_request("post", superuser)},
        )

        assert serializer.is_valid() is True
        assert serializer.validated_data["email"] == inactive_user_data["email"]
        assert serializer.validated_data["username"] == inactive_user_data["username"]
        assert serializer.validated_data["password"] == inactive_user_data["password"]
        assert serializer.validated_data["first_name"] == inactive_user_data["first_name"]
        assert serializer.validated_data["first_name"] == inactive_user_data["first_name"]
        assert serializer.validated_data["is_staff"] == inactive_user_data["is_staff"]
        assert serializer.validated_data["is_superuser"] == inactive_user_data["is_superuser"]

        assert "is_active" not in serializer.validated_data
