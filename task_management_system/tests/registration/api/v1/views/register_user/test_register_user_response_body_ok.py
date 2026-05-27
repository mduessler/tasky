from __future__ import annotations

import pytest
from django.urls import reverse

BASENAME = "register-user"


@pytest.mark.django_db
class TestResponseBodyOk:
    def test_post(self, register_data, api_client):
        url = reverse(BASENAME)

        response = api_client.post(url, data=register_data)

        assert response.status_code == 201
        assert set(response.data.keys()) == {"email", "username"}
