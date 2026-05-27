import pytest
from django.core.exceptions import PermissionDenied
from registration.api.v1.serializers import RegisterWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestServiceExceptions:
    def test_service_raises_error(self, register_data, monkeypatch):
        def mock_register_user(self, *args, **kwargs):
            raise PermissionDenied("Not allowed.")

        monkeypatch.setattr(
            "registration.services.RegistrationService.register_user",
            mock_register_user,
        )

        serializer = RegisterWriteSerializer(
            data=register_data, context={"request": build_request("post", None)}
        )
        assert serializer.is_valid() is True

        with pytest.raises(PermissionDenied) as exc:
            serializer.save()
        assert str(exc.value) == "Not allowed."
