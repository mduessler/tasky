import pytest
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from tms_auth.api.v1.serializers import JWTLogoutSerializer


@pytest.mark.django_db
class TestJWTLogoutSerializer:
    class TestDeserialization:
        def test_validates_input_correctly(self, active_user):
            refresh = RefreshToken.for_user(active_user)
            data = {"refresh": str(refresh)}

            serializer = JWTLogoutSerializer(data=data)

            assert serializer.is_valid() is True

    class TestValidation:
        def test_invalid_token(self):
            data = {"refresh": "not.a.valid.token"}
            serializer = JWTLogoutSerializer(data=data)

            with pytest.raises(TokenError, match="Token is invalid"):
                serializer.is_valid(raise_exception=True)

        def test_blacklisted_token(self, active_user):
            refresh = RefreshToken.for_user(active_user)

            refresh.blacklist()

            data = {"refresh": str(refresh)}
            serializer = JWTLogoutSerializer(data=data)

            with pytest.raises(TokenError):
                serializer.is_valid(raise_exception=True)

        def test_empty_token(self):
            data = {"refresh": ""}
            serializer = JWTLogoutSerializer(data=data)

            assert serializer.is_valid() is False
            assert "refresh" in serializer.errors

        def test_missing_token(self):
            data = {}
            serializer = JWTLogoutSerializer(data=data)

            assert serializer.is_valid() is False
            assert "refresh" in serializer.errors
