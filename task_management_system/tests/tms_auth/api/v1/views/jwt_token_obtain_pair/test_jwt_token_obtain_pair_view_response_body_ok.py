from __future__ import annotations

import pytest
from django.urls import reverse

BASENAME = "login-jwt"


@pytest.mark.django_db
class TestHttpMethods:
    @pytest.mark.parametrize("actor_fixture", ["active_user", "superuser"])
    def test_allowed(self, actor_fixture, request, api_client):
        actor = request.getfixturevalue(actor_fixture)
        data = request.getfixturevalue(f"{actor_fixture}_data")

        response = api_client.post(
            reverse(BASENAME), data={"email": actor.email, "password": data["password"]}
        )

        assert response.status_code == 200
        assert response.data["id"] == actor.id
        assert "access" in response.data.keys()
        assert "refresh" in response.data.keys()
