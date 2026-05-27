import pytest
from django.core.exceptions import ValidationError
from registration.validators import EmailMatcher


class TestEmailMatcher:
    def test_emails_match(self, active_user_data):
        assert EmailMatcher()(active_user_data["email"], active_user_data["email"]) is None

    def test_emails_does_not_match(self, inactive_user_data):
        with pytest.raises(ValidationError):
            EmailMatcher()("", inactive_user_data["email"])

    def test_no_email(self, active_user_data, inactive_user_data):
        with pytest.raises(ValidationError):
            EmailMatcher()(active_user_data["email"], inactive_user_data["email"])
