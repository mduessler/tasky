from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from django.contrib.auth.models import BaseUserManager

if TYPE_CHECKING:
    from .tms_user import TmsUser

U = TypeVar("U", bound="TmsUser")


class TmsUserManager(BaseUserManager[U]):  # type: ignore[misc]
    def create_user(
        self, email: str, username: str, password: str | None = None, **extra_fields: Any
    ) -> U:
        if not email:
            raise ValueError("Email required")
        user = self.model(email=self.normalize_email(email), username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user  # type: ignore[no-any-return]

    def create_superuser(
        self, email: str, username: str, password: str | None = None, **extra_fields: Any
    ) -> U:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff", False) and not extra_fields.get("is_superuser", False):
            raise ValueError("Superuser has is_staff and is_superuser false.")

        return self.create_user(email, username, password, **extra_fields)
