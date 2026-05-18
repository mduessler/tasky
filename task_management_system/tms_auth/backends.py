from typing import Any

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.http import HttpRequest
from user.models import TmsUser


class TmsEmailBackend(ModelBackend):  # type: ignore[misc]
    def authenticate(
        self,
        request: HttpRequest | None,
        password: str | None = None,
        email: str | None = None,
        **kwargs: Any
    ) -> TmsUser | None:
        login = email or kwargs.get("email")

        if login is None or password is None:
            return None

        try:
            user = TmsUser.objects.get(email__iexact=login)
        except TmsUser.DoesNotExist:
            check_password(password, "ThisIsAFakePasswordAgainstTiming.")
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
