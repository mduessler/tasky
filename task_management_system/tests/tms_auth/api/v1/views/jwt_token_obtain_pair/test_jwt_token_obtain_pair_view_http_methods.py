from __future__ import annotations

import pytest
from django.urls import reverse
from tms_auth.api.v1.serializers import JWTTokenObtainPairSerializer

BASENAME = "login-jwt"


@pytest.mark.django_db
class TestHttpMethods:
    @pytest.mark.parametrize("actor_fixture", ["active_user", "inactive_user", "superuser"])
    @pytest.mark.parametrize("method", ["post", "options"])
    def test_allowed(self, actor_fixture, method, request, api_client, monkeypatch):
        actor = request.getfixturevalue(actor_fixture)
        url = reverse(BASENAME)
        method_func = getattr(api_client, method)

        monkeypatch.setattr(
            JWTTokenObtainPairSerializer,
            "validate",
            lambda _, a: {"access": "fake_access", "refresh": "fake_refresh"},
        )

        if method == "post":
            data = request.getfixturevalue(f"{actor_fixture}_data")
            response = method_func(url, data={"email": actor.email, "password": data["password"]})
        else:
            response = method_func(url)

        assert response.status_code == 200

    @pytest.mark.parametrize("actor_fixture", ["active_user", "inactive_user", "superuser"])
    @pytest.mark.parametrize("method", ["delete", "get", "head", "put", "patch"])
    def test_not_allowed(self, actor_fixture, method, request, api_client):
        actor = request.getfixturevalue(actor_fixture)
        data = request.getfixturevalue(f"{actor_fixture}_data")
        url = reverse(BASENAME)
        method_func = getattr(api_client, method)

        if method == "post":
            response = method_func(url, data={"email": actor.email, "password": data["password"]})
        else:
            response = method_func(url)

        assert response.status_code == 405
