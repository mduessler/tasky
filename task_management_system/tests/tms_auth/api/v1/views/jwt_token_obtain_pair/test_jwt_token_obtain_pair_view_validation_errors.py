import pytest
from django.urls import reverse

BASENAME = "login-jwt"


@pytest.mark.django_db
class TestValidationError:
    def test_invalid_credentials(self, active_user, api_client):
        url = reverse(BASENAME)
        response = api_client.post(url)

        assert response.status_code == 400
