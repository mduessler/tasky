from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField, CharField, DateTimeField, EmailField

from .tms_user_manager import TmsUserManager


class TmsUser(AbstractUser):  # type: ignore[misc]
    email = EmailField(unique=True, blank=False)
    username = CharField(max_length=128, unique=False)
    is_active = BooleanField(default=False)
    is_staff = BooleanField(default=False)
    date_joined = DateTimeField(auto_now=True)

    objects: TmsUserManager["TmsUser"] = TmsUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.email  # type: ignore[no-any-return]

    # def get_absolute_url(self) -> str:
    #     return reverse("user-profile", args=[self.id])  # type: ignore[attr-defined]
