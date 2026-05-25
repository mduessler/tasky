import pytest
from tests.utils import build_request
from user.api.v1.serializers import TmsUserReadSerializer
from user.policies import TmsUserPolicy


@pytest.mark.django_db
class TestRepresentation:
    def test_serializes_expected_fields(self, active_user_read_only, inactive_user_read_only):
        serializer = TmsUserReadSerializer(
            instance=inactive_user_read_only,
            context={"request": build_request("get", active_user_read_only)},
        )

        assert serializer.data["id"] == inactive_user_read_only.id
        assert serializer.data["email"] == inactive_user_read_only.email
        assert serializer.data["username"] == inactive_user_read_only.username
        assert serializer.data["first_name"] == inactive_user_read_only.first_name
        assert serializer.data["last_name"] == inactive_user_read_only.last_name
        assert serializer.data["can_delete"] == TmsUserPolicy.can_delete(
            active_user_read_only, inactive_user_read_only
        )
        assert serializer.data["editable_fields"] == list(
            TmsUserPolicy.get_editable_fields(active_user_read_only, inactive_user_read_only)
        )

        assert "password" not in serializer.data
        assert "is_active" not in serializer.data
        assert "is_staff" not in serializer.data
        assert "is_superuser" not in serializer.data
