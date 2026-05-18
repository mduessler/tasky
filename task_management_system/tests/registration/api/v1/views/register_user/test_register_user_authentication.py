from __future__ import annotations

import pytest
from django.urls import reverse

BASENAME = "register-user"


@pytest.mark.django_db
class TestAuthentication:
    def test_unauthenticated_actor_allowed(self, inactive_user_data, api_client):
        url = reverse(BASENAME)
        response = api_client.post(url, data=inactive_user_data)

        assert response.status_code != 401

    @pytest.mark.parametrize("actor_fixture", ["active_user", "inactive_user", "superuser"])
    def test_authenticated_actor_not_allowed(
        self, actor_fixture, request, inactive_user_data, api_client
    ):
        actor = request.getfixturevalue(actor_fixture)
        url = reverse(BASENAME)

        api_client.force_authenticate(user=actor)
        response = api_client.post(url, data=inactive_user_data)

        assert response.status_code == 403

    def test_expired_token_not_allowed(
        self, inactive_user, inactive_user_data, api_client, access_token_factory
    ):
        url = reverse(BASENAME)

        expired_token = access_token_factory(user=inactive_user, expired=True)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired_token}")
        response = api_client.post(url, data=inactive_user_data)

        assert response.status_code == 401
        assert set(response.data.keys()) == {"code", "detail", "messages"}
        assert str(response.data["detail"]) == "Given token not valid for any token type"

    def test_invalid_token_not_allowed(self, inactive_user_data, api_client):
        url = reverse(BASENAME)
        api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.value")

        response = api_client.post(url, data=inactive_user_data)

        assert response.status_code == 401
        assert set(response.data.keys()) == {"code", "detail", "messages"}
        assert str(response.data["detail"]) == "Given token not valid for any token type"
