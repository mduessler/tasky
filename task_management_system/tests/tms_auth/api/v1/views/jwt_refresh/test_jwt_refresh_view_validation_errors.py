import pytest
from django.urls import reverse

BASENAME = "refresh-jwt"


@pytest.mark.django_db
class TestValidationError:
    def test_missing_refresh_token(self, api_client, active_user, refresh_token_factory):
        refresh_token_factory(active_user)
        response = api_client.post(reverse(BASENAME), data={})

        assert response.status_code == 400
