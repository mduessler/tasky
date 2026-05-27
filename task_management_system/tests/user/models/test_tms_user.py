import pytest
from django.db import IntegrityError
from user.models import TmsUser


@pytest.mark.django_db
class TestTmsUserModel:
    def test_create_user_success(self, active_user_data):
        user = TmsUser.objects.create_user(**active_user_data)

        assert user.email == active_user_data["email"].lower()
        assert user.username == active_user_data["username"]
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password(active_user_data["password"])

    def test_create_superuser_success(self, active_user_data):
        admin = TmsUser.objects.create_superuser(**active_user_data)

        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.is_active is True

    def test_email_is_normalized(self, active_user_data):
        active_user_data["email"] = "USER@EXAMPLE.COM"
        user = TmsUser.objects.create_user(**active_user_data)
        assert user.email == "USER@example.com"

    def test_create_user_no_email_raises_error(self):
        with pytest.raises(ValueError, match="Email required"):
            TmsUser.objects.create_user(email="", username="user", password="123")

    def test_duplicate_email_raises_integrity_error(self, active_user_data):
        TmsUser.objects.create_user(**active_user_data)

        with pytest.raises(IntegrityError):
            TmsUser.objects.create_user(**active_user_data)

    def test_superuser_invalid_flags_raise_error(self, active_user_data):
        extra_fields = active_user_data.copy()

        extra_fields["is_staff"] = False
        extra_fields["is_superuser"] = False

        password = extra_fields.pop("password")
        email = extra_fields.pop("email")

        with pytest.raises(ValueError):
            TmsUser.objects.create_superuser(email=email, password=password, **extra_fields)

    def test_str_representation(self, active_user):
        assert str(active_user) == active_user.email
