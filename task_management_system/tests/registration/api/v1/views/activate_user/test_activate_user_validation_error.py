from __future__ import annotations

import pytest
from django.urls import reverse

BASENAME = "activate-user"


@pytest.mark.django_db
class TestValidationError:
    def test_post(self, api_client):
        data = {"email": "", "token": ""}

        url = reverse(BASENAME)

        response = api_client.post(url, data=data)

        assert response.status_code == 400
