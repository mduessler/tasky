from __future__ import annotations

import pytest
from tests.utils import parse_url

BASENAME = "user"


@pytest.mark.django_db
class TestValidationError:
    def test_patch(self, superuser, active_user, api_client):
        old_username = active_user.username

        data = {"username": ""}
        url = parse_url(BASENAME, "detail", active_user.id)

        api_client.force_authenticate(user=superuser)
        response = api_client.patch(url, data=data)

        active_user.refresh_from_db()
        assert response.status_code == 400
        assert set(response.data.keys()) == {"username"}
        assert str(response.data["username"][0]) == "This field may not be blank."
        assert active_user.username == old_username
