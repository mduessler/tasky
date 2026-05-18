import pytest
from django.urls import reverse

BASENAME = "logout-jwt"


@pytest.mark.django_db
class TestResponseBodyOk:
    def test_valid_logout(
        self, api_client, active_user, access_token_factory, refresh_token_factory
    ):
        url = reverse(BASENAME)
        access = access_token_factory(active_user)
        refresh = refresh_token_factory(active_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(url, data={"refresh": refresh})

        assert response.status_code == 200
        assert response.data == {}
