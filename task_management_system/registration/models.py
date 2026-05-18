from __future__ import annotations

from datetime import timedelta
from secrets import randbelow
from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import CASCADE, CharField, DateTimeField, ForeignKey, Model, UniqueConstraint
from django.utils.timezone import now
from user.models import TmsUser


class EmailVerificationToken(Model):  # type: ignore[misc]
    token = CharField(max_length=6, editable=False)
    user: ForeignKey[EmailVerificationToken, TmsUser] = ForeignKey(TmsUser, on_delete=CASCADE)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    expires_at = DateTimeField(auto_created=True, editable=False)

    class Meta:
        constraints = [UniqueConstraint(fields=["user"], name="unique_user_token")]

    def clean(self) -> None:
        if self.user and self.user.is_active:
            raise ValidationError("User already activated.")
        return super().clean()  # type: ignore[no-any-return]

    def generate_token(self) -> None:
        if not self.token:
            self.token = "".join(str(randbelow(10)) for _ in range(6))

    def is_expired(self) -> bool:
        return now() > self.expires_at  # type: ignore[no-any-return]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk:
            raise ValidationError(
                "Cannot update an existing token. Tokens are immutable and can only be deleted."
            )

        self.generate_token()
        self.expires_at = now() + timedelta(minutes=15)

        super().save(*args, **kwargs)
