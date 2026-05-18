from __future__ import annotations

import pytest
from tests.utils import parse_url

BASENAME = "user"


@pytest.mark.django_db
class TestHttpMethods:
    @pytest.mark.parametrize(
        "method, expected, url_name",
        [
            ("get", 200, "list"),
            ("options", 200, "list"),
            ("head", 200, "list"),
            ("get", 200, "detail"),
            ("patch", 200, "detail"),
            ("delete", 204, "detail"),
            ("get", 200, "tasks"),
            ("get", 200, "task-memberships"),
            ("get", 200, "task-notes"),
        ],
    )
    def test_allowed(self, method, expected, url_name, superuser, api_client):
        data = {"username": "XoXoXo"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, superuser.id)

        api_client.force_authenticate(user=superuser)
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == expected

    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("post", "list"),
            ("put", "detail"),
            ("post", "tasks"),
            ("patch", "tasks"),
            ("delete", "tasks"),
            ("put", "tasks"),
            ("post", "task-memberships"),
            ("patch", "task-memberships"),
            ("delete", "task-memberships"),
            ("put", "task-memberships"),
            ("post", "task-notes"),
            ("patch", "task-notes"),
            ("delete", "task-notes"),
            ("put", "task-notes"),
        ],
    )
    def test_forbidden(self, method, url_name, superuser, api_client):
        data = {"username": "XoXoXo"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, superuser.id)

        api_client.force_authenticate(user=superuser)
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 405
