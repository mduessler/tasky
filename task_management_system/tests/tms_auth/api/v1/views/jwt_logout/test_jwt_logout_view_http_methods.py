from __future__ import annotations

import pytest
from django.urls import reverse
from tms_auth.api.v1.serializers import JWTLogoutSerializer

BASENAME = "logout-jwt"


@pytest.mark.django_db
class TestHttpMethods:
    @pytest.mark.parametrize("method", ["post", "options"])
    def test_allowed(self, method, api_client, active_user, access_token_factory, monkeypatch):
        url = reverse(BASENAME)
        method_func = getattr(api_client, method)
        access = access_token_factory(active_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        monkeypatch.setattr(JWTLogoutSerializer, "validate", lambda _, a: {})

        if method == "post":
            response = method_func(url, data={"refresh": "fake_refresh_token"})
        else:
            response = method_func(url)

        assert response.status_code == 200

    @pytest.mark.parametrize("method", ["delete", "get", "head", "put", "patch"])
    def test_not_allowed(self, method, api_client, active_user, access_token_factory):
        url = reverse(BASENAME)
        method_func = getattr(api_client, method)
        access = access_token_factory(active_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = method_func(url)

        assert response.status_code == 405
