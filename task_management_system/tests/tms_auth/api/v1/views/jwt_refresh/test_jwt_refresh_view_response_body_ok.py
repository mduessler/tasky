import pytest
from django.urls import reverse

BASENAME = "refresh-jwt"


@pytest.mark.django_db
class TestResponseBodyOk:
    def test_valid_token(self, api_client, active_user, refresh_token_factory):
        token = refresh_token_factory(active_user)
        response = api_client.post(reverse(BASENAME), data={"refresh": token})

        assert response.status_code == 200
        assert "access" in response.data.keys()
        assert "refresh" in response.data.keys()
