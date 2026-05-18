import pytest
from user.models import TmsUser


@pytest.mark.django_db
class TestTmsUserManager:
    def test_create_user_normalizes_email(self):
        email = "MAX.MUST@EXAMPLE.COM"
        expected_email = "MAX.MUST@example.com"
        user = TmsUser.objects.create_user(email=email, username="max", password="secure_password")
        assert user.email == expected_email

    def test_create_user_requires_email(self):
        with pytest.raises(ValueError) as excinfo:
            TmsUser.objects.create_user(email="", username="test", password="123")
        assert "Email required" in str(excinfo.value)

    def test_create_user_requires_username(self):
        with pytest.raises(TypeError):
            TmsUser.objects.create_user(email="test@example.com", password="123")

    def test_create_superuser_sets_correct_flags(self):
        admin = TmsUser.objects.create_superuser(
            email="admin@example.com", username="admin", password="admin_password"
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.is_active is False

    def test_create_superuser_fails_with_invalid_flags(self, active_user_data):
        extra_fields = active_user_data.copy()

        extra_fields["is_staff"] = False
        extra_fields["is_superuser"] = False

        password = extra_fields.pop("password")
        email = extra_fields.pop("email")

        with pytest.raises(ValueError):
            TmsUser.objects.create_superuser(email=email, password=password, **extra_fields)

    def test_manager_uses_correct_db(self, active_user_data):
        TmsUser.objects.create_user(**active_user_data)
        assert TmsUser.objects.filter(email=active_user_data["email"]).exists() is True
