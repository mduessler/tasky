from __future__ import annotations

import pytest
from tests.utils import parse_url

BASENAME = "user"


@pytest.mark.django_db
class TestAuthentication:
    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("get", "list"),
            ("options", "list"),
            ("head", "list"),
            ("get", "detail"),
            ("patch", "detail"),
            ("delete", "detail"),
            ("get", "tasks"),
            ("get", "task-memberships"),
            ("get", "task-notes"),
        ],
    )
    def test_unauthenticate_actor_not_allowed(
        self, method, url_name, superuser_read_only, api_client
    ):
        data = {"username": "XoXoXo"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, superuser_read_only.id)

        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 401

    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("get", "list"),
            ("head", "list"),
            ("get", "detail"),
            ("patch", "detail"),
            ("delete", "detail"),
            ("get", "tasks"),
            ("get", "task-memberships"),
            ("get", "task-notes"),
        ],
    )
    def test_authenticated_actor_allowed_permission_denied(
        self, method, url_name, active_user, superuser_read_only, api_client
    ):
        data = {"username": "XoXoXo"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, superuser_read_only.id)

        api_client.force_authenticate(user=active_user)
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("get", "list"),
            ("get", "detail"),
            ("patch", "detail"),
            ("delete", "detail"),
            ("get", "tasks"),
            ("get", "task-memberships"),
            ("get", "task-notes"),
        ],
    )
    def test_expired_token_not_allowed(
        self,
        method,
        url_name,
        superuser_read_only,
        api_client,
        access_token_factory,
    ):
        data = {"username": "XoXoXo"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, superuser_read_only.id)

        expired_token = access_token_factory(user=superuser_read_only, expired=True)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired_token}")
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 401
        assert set(response.data.keys()) == {"code", "detail", "messages"}
        assert str(response.data["detail"]) == "Given token not valid for any token type"

    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("get", "list"),
            ("get", "detail"),
            ("patch", "detail"),
            ("delete", "detail"),
            ("get", "tasks"),
            ("get", "task-memberships"),
            ("get", "task-notes"),
        ],
    )
    def test_invalid_token_not_allowed(
        self,
        method,
        url_name,
        superuser_read_only,
        api_client,
    ):

        data = {"username": "XoXoXo"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, superuser_read_only.id)

        api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.value")
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 401
        assert set(response.data.keys()) == {"code", "detail", "messages"}
        assert str(response.data["detail"]) == "Given token not valid for any token type"
