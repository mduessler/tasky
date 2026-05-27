import pytest
from tests.utils import parse_url

BASENAME = "note"


@pytest.mark.django_db
class TestAuthentication:
    @pytest.fixture(scope="class", autouse=True)
    def preload(
        self,
        member_is_owner_read_only,
        member_is_admin_read_only,
        member_is_member_read_only,
        member_is_viewer_read_only,
        user_is_not_member_read_only,
        superuser_read_only,
    ):
        pass

    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("get", "list"),
            ("options", "list"),
            ("head", "list"),
            ("get", "detail"),
            ("patch", "detail"),
            ("delete", "detail"),
        ],
    )
    def test_unauthenticated_actor_not_allowed(
        self, method, url_name, task_note_read_only, api_client
    ):
        data = {"note": "updated note"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, task_note_read_only.id)

        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 401

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_get_list_permission_denied(self, actor_fixture, request, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)

        url = parse_url(BASENAME, "list")

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("head", "list"),
            ("get", "detail"),
        ],
    )
    def test_safe_methods_not_allowed(
        self, user_is_not_member_read_only, task_note_read_only, method, url_name, api_client
    ):
        actor, _ = user_is_not_member_read_only

        url = parse_url(BASENAME, url_name, task_note_read_only.id)

        api_client.force_authenticate(user=actor)
        response = getattr(api_client, method)(url)

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_delete_permission_denied(
        self, actor_fixture, request, task_note_read_only, api_client
    ):
        actor, _ = request.getfixturevalue(actor_fixture)

        url = parse_url(BASENAME, "detail", task_note_read_only.id)

        api_client.force_authenticate(user=actor)
        response = api_client.delete(url)

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_patch_permission_denied(
        self, actor_fixture, request, task_note_read_only, api_client
    ):
        actor, _ = request.getfixturevalue(actor_fixture)

        url = parse_url(BASENAME, "detail", task_note_read_only.id)
        data = {"note": "updated note"}

        api_client.force_authenticate(user=actor)
        response = api_client.patch(url, data=data)

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("get", "list"),
            ("get", "detail"),
            ("patch", "detail"),
            ("delete", "detail"),
        ],
    )
    def test_expired_token_not_allowed(
        self,
        method,
        url_name,
        superuser_read_only,
        task_note_read_only,
        api_client,
        access_token_factory,
    ):
        data = {"note": "updated note"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, task_note_read_only.id)

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
        ],
    )
    def test_invalid_token_not_allowed(self, method, url_name, task_note_read_only, api_client):
        data = {"note": "updated note"} if method == "patch" else {}
        url = parse_url(BASENAME, url_name, task_note_read_only.id)

        api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.value")

        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 401
        assert set(response.data.keys()) == {"code", "detail", "messages"}
        assert str(response.data["detail"]) == "Given token not valid for any token type"
