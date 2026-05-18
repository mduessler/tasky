import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

BASENAME = "refresh-jwt"


@pytest.mark.django_db
class TestAuthentication:
    url = reverse(BASENAME)

    def test_invalid_refresh_token(self, api_client, active_user, refresh_token_factory):
        refresh_token_factory(active_user)
        response = api_client.post(self.url, data={"refresh": "invalid_token"})

        assert response.status_code == 401

    def test_expired_refresh_token(self, api_client, active_user, refresh_token_factory):
        token = refresh_token_factory(active_user, expired=True)
        response = api_client.post(self.url, data={"refresh": token})

        assert response.status_code == 401

    def test_blacklisted_refresh_token(self, api_client, active_user, refresh_token_factory):
        refresh = refresh_token_factory(active_user)

        token = RefreshToken(refresh)
        token.blacklist()

        response = api_client.post(self.url, data={"refresh": refresh})
        assert response.status_code == 401
