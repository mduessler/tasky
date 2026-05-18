import pytest
from rest_framework.exceptions import ValidationError
from tests.utils import build_request
from user.api.v1.serializers import TmsUserWriteSerializer
from user.services import TmsUserService


@pytest.mark.django_db
class TestServiceExceptions:
    def test_update_service_raises_error(
        self, active_user, inactive_user, monkeypatch, inactive_user_data
    ):
        def mock_update(self, *args, **kwargs):
            raise ValidationError({"detail": "Limit reached"})

        monkeypatch.setattr(TmsUserService, "update", mock_update)

        serializer = TmsUserWriteSerializer(
            instance=inactive_user,
            data=inactive_user_data,
            context={"request": build_request("post", active_user)},
        )

        assert serializer.is_valid() is True
        with pytest.raises(ValidationError) as exc:
            serializer.save()

        assert exc.value.detail["detail"] == "Limit reached"
