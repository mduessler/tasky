from __future__ import annotations

import pytest
from django.urls import reverse
from tms_auth.api.v1.serializers import JWTRefreshSerializer

BASENAME = "refresh-jwt"


@pytest.mark.django_db
class TestHttpMethods:
    @pytest.mark.parametrize("method", ["post", "options"])
    def test_allowed(self, method, api_client, monkeypatch):
        url = reverse(BASENAME)
        method_func = getattr(api_client, method)

        monkeypatch.setattr(
            JWTRefreshSerializer, "validate", lambda _, a: {"access": "fake_access"}
        )

        if method == "post":
            response = method_func(url, data={"refresh": "fake_refresh_token"})
        else:
            response = method_func(url)

        assert response.status_code == 200

    @pytest.mark.parametrize("method", ["delete", "get", "head", "put", "patch"])
    def test_not_allowed(self, method, api_client):
        url = reverse(BASENAME)
        method_func = getattr(api_client, method)

        response = method_func(url)

        assert response.status_code == 405
