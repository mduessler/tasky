import pytest
from django.urls import reverse
from registration.api.v1.permissions import ActivateUserPermission

BASENAME = "activate-user"


@pytest.mark.django_db
class TestPermissionDenied:
    @pytest.mark.parametrize("actor_fixture", ["active_user", "inactive_user", "superuser"])
    def test_actor_has_no_permission(
        self,
        actor_fixture,
        request,
        inactive_user_data,
        api_client,
        monkeypatch,
    ):
        actor = request.getfixturevalue(actor_fixture)
        url = reverse(BASENAME)

        monkeypatch.setattr(ActivateUserPermission, "has_permission", lambda p, r, v: False)

        api_client.force_authenticate(user=actor)
        response = api_client.post(url, data=inactive_user_data)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == "You do not have permission to perform this action."
