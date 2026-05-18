from typing import Any

from registration.services import RegistrationService
from registration.validators import EmailMatcher, PasswordMatcher
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import CharField, EmailField, ModelSerializer
from user.models import TmsUser


class RegisterWriteSerializer(ModelSerializer):  # type: ignore[misc]
    email_verification = EmailField(write_only=True)
    password = CharField(write_only=True, min_length=8)
    password_verification = CharField(write_only=True, min_length=8)

    class Meta:
        model = TmsUser
        fields = [
            "username",
            "email",
            "email_verification",
            "password",
            "password_verification",
            "first_name",
            "last_name",
        ]
        read_only_fields: list[str] = []

    def validate_email_verification(self, value: str) -> str:
        try:
            email = self.initial_data.get("email")
            EmailMatcher()(email, value)
        except ValidationError:
            raise ValidationError("Emails do not match.")
        return value

    def validate_password_verification(self, value: str) -> str:
        try:
            password = self.initial_data.get("password")
            PasswordMatcher()(password, value)
        except ValidationError:
            raise ValidationError("Passwords do not match.")
        return value

    def create(self, validated_data: dict[str, Any]) -> TmsUser:
        validated_data.pop("email_verification")
        validated_data.pop("password_verification")
        return RegistrationService.register_user(validated_data)
