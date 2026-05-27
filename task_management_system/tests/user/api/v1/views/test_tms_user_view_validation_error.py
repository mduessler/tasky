from __future__ import annotations

import pytest
from tests.utils import parse_url

BASENAME = "user"


@pytest.mark.django_db
class TestValidationError:
    def test_patch(self, superuser_read_only, active_user_read_only, api_client):
        old_username = active_user_read_only.username

        data = {"username": ""}
        url = parse_url(BASENAME, "detail", active_user_read_only.id)

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.patch(url, data=data)

        active_user_read_only.refresh_from_db()
        assert response.status_code == 400
        assert set(response.data.keys()) == {"username"}
        assert str(response.data["username"][0]) == "This field may not be blank."
        assert active_user_read_only.username == old_username
