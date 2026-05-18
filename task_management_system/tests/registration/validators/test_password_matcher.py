import pytest
from django.core.exceptions import ValidationError
from registration.validators import PasswordMatcher


class TestPasswordMatcher:
    def test_password_match(self):
        assert PasswordMatcher()("equal", "equal") is None

    def test_no_password(self):
        with pytest.raises(ValidationError):
            PasswordMatcher()("", "unequal")

    def test_password_does_not_match(self):
        with pytest.raises(ValidationError):
            PasswordMatcher()("not-matching", "password.")
