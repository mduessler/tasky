import pytest
from django.urls import reverse

BASENAME = "logout-jwt"


@pytest.mark.django_db
class TestValidationError:
    def test_missing_refresh_token(self, api_client, active_user, access_token_factory):
        url = reverse(BASENAME)
        access = access_token_factory(active_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(url, data={})

        assert response.status_code == 400
