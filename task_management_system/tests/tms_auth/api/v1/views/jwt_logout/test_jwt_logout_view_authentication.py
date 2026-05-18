import pytest
from django.urls import reverse

BASENAME = "logout-jwt"


@pytest.mark.django_db
class TestAuthentication:
    url = reverse(BASENAME)

    def test_valid_logout(
        self, api_client, active_user, access_token_factory, refresh_token_factory
    ):
        access = access_token_factory(active_user)
        refresh = refresh_token_factory(active_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(self.url, data={"refresh": refresh})

        assert response.status_code == 200

    def test_expired_access_token(
        self, api_client, active_user, access_token_factory, refresh_token_factory
    ):
        access = access_token_factory(active_user, expired=True)
        refresh = refresh_token_factory(active_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(self.url, data={"refresh": refresh})

        assert response.status_code == 401

    def test_invalid_access_token(self, api_client, active_user, refresh_token_factory):
        refresh = refresh_token_factory(active_user)
        api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token")
        response = api_client.post(self.url, data={"refresh": refresh})

        assert response.status_code == 401

    def test_unauthenticated_request_is_denied(
        self, api_client, active_user, refresh_token_factory
    ):
        refresh = refresh_token_factory(active_user)
        response = api_client.post(self.url, data={"refresh": refresh})

        assert response.status_code == 401

    def test_inactive_user_is_denied(
        self, api_client, inactive_user, access_token_factory, refresh_token_factory
    ):
        access = access_token_factory(inactive_user)
        refresh = refresh_token_factory(inactive_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(self.url, data={"refresh": refresh})

        assert response.status_code == 401
