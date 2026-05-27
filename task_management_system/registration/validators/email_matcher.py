from django.forms import ValidationError
from django.utils.deconstruct import deconstructible

from task_management_system.utils import ERROR_MESSAGES


@deconstructible
class EmailMatcher:
    invalid = "email-not-match"

    def __call__(self, email: str, email_verification: str) -> None:
        if not email or not email_verification:
            raise ValidationError(ERROR_MESSAGES[self.invalid], code=self.invalid)
        if email.lower() != email_verification.lower():
            raise ValidationError(ERROR_MESSAGES[self.invalid], code=self.invalid)
