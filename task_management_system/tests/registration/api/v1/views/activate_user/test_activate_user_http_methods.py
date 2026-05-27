from __future__ import annotations

import pytest
from django.urls import reverse

BASENAME = "activate-user"


@pytest.mark.django_db
class TestHttpMethods:
    @pytest.mark.parametrize("method, expected", [("options", 200), ("post", 202)])
    def test_allowed(self, method, expected, email_token, api_client):
        url = reverse(BASENAME)
        data = {"email": email_token.user.email, "token": email_token.token}

        if method == "post":
            response = api_client.post(url, data=data)
        else:
            response = getattr(api_client, method)(url)
        assert response.status_code == expected

    @pytest.mark.parametrize(
        "method, expected",
        [("get", 401), ("head", 405), ("put", 401), ("patch", 401), ("delete", 401)],
    )
    def test_forbidden(self, method, expected, email_token, api_client):
        url = reverse(BASENAME)
        data = {"email": email_token.user.email, "token": email_token.token}

        if method in ["patch", "put"]:
            response = getattr(api_client, method)(url, data=data)
        else:
            response = getattr(api_client, method)(url)

        assert response.status_code == expected
