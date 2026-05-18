from django.forms import ValidationError
from django.utils.deconstruct import deconstructible

from task_management_system.utils import ERROR_MESSAGES


@deconstructible
class PasswordMatcher:
    invalid = "password-not-match"

    def __call__(self, password: str, password_verification: str) -> None:
        if not password or not password_verification:
            raise ValidationError(ERROR_MESSAGES[self.invalid], code=self.invalid)
        if password != password_verification:
            raise ValidationError(ERROR_MESSAGES[self.invalid], code=self.invalid)
