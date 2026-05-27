import pytest
from django.urls import reverse

BASENAME = "login-jwt"


@pytest.mark.django_db
class TestAuthentication:
    url = reverse(BASENAME)

    def test_invalid_credentials(self, api_client, active_user):
        response = api_client.post(
            self.url, data={"email": active_user.email, "password": "invalid"}
        )
        assert response.status_code == 401

    def test_inactive_user(self, api_client, inactive_user, inactive_user_data):
        response = api_client.post(
            self.url,
            data={"email": inactive_user.email, "password": inactive_user_data["password"]},
        )
        assert response.status_code == 401

    def test_post_with_nonexistent_user_returns_401(self, api_client, users):
        response = api_client.post(
            self.url, data={"email": "invalid@email.com", "password": "invalid"}
        )
        assert response.status_code == 401
