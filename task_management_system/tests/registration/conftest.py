import pytest
from registration.models import EmailVerificationToken


@pytest.fixture
def data():
    return {
        "email": "important@fake.de",
        "username": "Mr Imporant",
        "password": "SuperSecure.",
        "first_name": "Max",
        "last_name": "Robert",
    }


@pytest.fixture
def register_data(inactive_user_data):
    return {
        "email": inactive_user_data["email"],
        "email_verification": inactive_user_data["email"],
        "username": inactive_user_data["username"],
        "password": inactive_user_data["password"],
        "password_verification": inactive_user_data["password"],
        "first_name": "Max",
        "last_name": "Rober",
    }


@pytest.fixture
@pytest.mark.django_db
def email_token(inactive_user):
    token = EmailVerificationToken(user=inactive_user)
    token.full_clean()
    token.save()

    return token


@pytest.fixture
def activate_data(email_token):
    return {"email": email_token.user.email, "token": email_token.token}
