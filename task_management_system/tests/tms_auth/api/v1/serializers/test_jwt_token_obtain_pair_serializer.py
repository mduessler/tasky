import pytest
from rest_framework.exceptions import AuthenticationFailed
from tms_auth.api.v1.serializers import JWTTokenObtainPairSerializer


@pytest.mark.django_db
class TestJwtTokenObtainPairSerializer:

    class TestDeserialization:
        def test_validates_input_correctly(self, active_user, active_user_data):
            data = {"email": active_user.email, "password": active_user_data["password"]}

            serializer = JWTTokenObtainPairSerializer(data=data)

            assert serializer.is_valid() is True
            assert serializer.user == active_user
            assert serializer.validated_data["id"] == active_user.id
            assert "access" in serializer.validated_data
            assert "refresh" in serializer.validated_data

    class TestRepresenation:
        def test_serializes_expected_fields(self, active_user, active_user_data):
            data = {"email": active_user.email, "password": active_user_data["password"]}
            serializer = JWTTokenObtainPairSerializer(data=data)

            assert serializer.is_valid() is True
            assert serializer.validated_data["id"] == active_user.id
            assert "access" in serializer.validated_data
            assert "refresh" in serializer.validated_data

    class TestValidation:
        def test_deserialization_invalid_email(self):
            data = {"email": "invalid", "password": "ThisIsATestingPassword"}
            serializer = JWTTokenObtainPairSerializer(data=data)

            with pytest.raises(AuthenticationFailed):
                serializer.is_valid(raise_exception=True)

        def test_deserialization_invalid_password(self, active_user):
            data = {"email": active_user.email, "password": "invalid"}
            serializer = JWTTokenObtainPairSerializer(data=data)

            with pytest.raises(AuthenticationFailed):
                serializer.is_valid(raise_exception=True)

        def test_deserialization_empty_password(self, active_user):
            data = {"email": active_user.email, "password": ""}
            serializer = JWTTokenObtainPairSerializer(data=data)

            assert serializer.is_valid() is False
            assert "password" in serializer.errors
