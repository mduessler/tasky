from __future__ import annotations

import pytest
from django.urls import reverse

BASENAME = "register-user"


@pytest.mark.django_db
class TestHttpMethods:
    @pytest.mark.parametrize("method, expected", [("options", 200), ("post", 201)])
    def test_post_allowed(self, method, expected, register_data, api_client):
        url = reverse(BASENAME)

        if method == "post":
            response = api_client.post(url, data=register_data)
        else:
            response = getattr(api_client, method)(url)
        assert response.status_code == expected

    @pytest.mark.parametrize(
        "method, expected",
        [("get", 401), ("head", 405), ("put", 401), ("patch", 401), ("delete", 401)],
    )
    def test_forbidden(self, method, expected, api_client):
        url = reverse(BASENAME)

        response = getattr(api_client, method)(url)

        assert response.status_code == expected
