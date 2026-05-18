import pytest
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from tms_auth.api.v1.serializers import JWTRefreshSerializer


@pytest.mark.django_db
class TestJWTRefreshSerializer:
    class TestDeserialization:
        def test_validates_input_correctly(self, active_user):
            refresh = RefreshToken.for_user(active_user)
            data = {"refresh": str(refresh)}

            serializer = JWTRefreshSerializer(data=data)

            assert serializer.is_valid() is True
            assert "access" in serializer.validated_data
            assert "refresh" in serializer.validated_data

    class TestValidation:
        def test_invalid_token(self):
            data = {"refresh": "invalid"}
            serializer = JWTRefreshSerializer(data=data)

            with pytest.raises(TokenError, match="Token is invalid"):
                serializer.is_valid(raise_exception=True)

        def test_expired_or_blacklisted_token(self, active_user):
            refresh = RefreshToken.for_user(active_user)

            refresh.blacklist()

            data = {"refresh": str(refresh)}
            serializer = JWTRefreshSerializer(data=data)

            with pytest.raises(TokenError):
                serializer.is_valid(raise_exception=True)

        def test_wrong_token_type(self, active_user):
            access = str(RefreshToken.for_user(active_user).access_token)

            data = {"refresh": access}
            serializer = JWTRefreshSerializer(data=data)

            with pytest.raises(TokenError, match="Token has wrong type"):
                serializer.is_valid(raise_exception=True)

        def test_missing_token(self):
            data = {}
            serializer = JWTRefreshSerializer(data=data)

            assert serializer.is_valid() is False
            assert "refresh" in serializer.errors
