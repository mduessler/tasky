from __future__ import annotations

import pytest
from tests.utils import parse_url
from user.errors import USER_DOES_NOT_EXIST

BASENAME = "user"


@pytest.mark.django_db
class TestNotFound:
    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("delete", "detail"),
            ("get", "detail"),
            ("patch", "detail"),
            ("get", "tasks"),
            ("get", "task-memberships"),
            ("get", "task-notes"),
        ],
    )
    def test_detail(self, method, url_name, superuser_read_only, api_client):
        data = {"username": "XoXoXo"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, 9999)

        api_client.force_authenticate(user=superuser_read_only)
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 404
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == USER_DOES_NOT_EXIST
