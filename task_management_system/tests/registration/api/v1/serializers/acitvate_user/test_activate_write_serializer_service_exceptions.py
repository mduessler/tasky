import pytest
from django.core.exceptions import PermissionDenied
from registration.api.v1.serializers import ActivateWriteSerializer
from tests.utils import build_request


@pytest.mark.django_db
class TestServiceExceptions:
    def test_service_raises_error(self, email_token, monkeypatch):
        def mock_active_user(*args, **kwargs):
            raise PermissionDenied("Not allowed.")

        data = {"email": email_token.user.email, "token": email_token.token}
        monkeypatch.setattr(
            "registration.services.RegistrationService.activate_user", mock_active_user
        )

        serializer = ActivateWriteSerializer(
            data=data, context={"request": build_request("post", None)}
        )
        assert serializer.is_valid() is True

        with pytest.raises(PermissionDenied) as exc:
            serializer.save()
        assert str(exc.value) == "Not allowed."
