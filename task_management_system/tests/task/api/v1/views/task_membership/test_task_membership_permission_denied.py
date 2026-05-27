from __future__ import annotations

import pytest
from task.errors import (
    PERMISSION_DENIED_TO_DELETE_TASK_MEMBERSHIP,
    PERMISSION_DENIED_TO_UPDATE_TASK_MEMBERSHIP,
    PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP,
)
from task.policies import TaskMembershipPolicy
from tests.utils import parse_url

BASENAME = "membership"


@pytest.mark.django_db
class TestPermissionDenied:
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
        "actor_fixture",
        [
            "member_is_owner_read_only",
            "member_is_admin_read_only",
            "member_is_member_read_only",
            "member_is_viewer_read_only",
        ],
    )
    def test_list_actor_has_no_permission(self, actor_fixture, request, api_client):
        actor, _ = request.getfixturevalue(actor_fixture)
        url = parse_url(BASENAME, "list")

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) in {
            "You do not have permission to perform this action.",
            PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP,
        }

    def test_retrieve_actor_has_no_permission(
        self, user_is_not_member_read_only, task_membership_read_only, api_client, monkeypatch
    ):
        actor, _ = user_is_not_member_read_only
        url = parse_url(BASENAME, "detail", task_membership_read_only.id)

        monkeypatch.setattr(TaskMembershipPolicy, "can_view", lambda a, u: False)

        api_client.force_authenticate(user=actor)
        response = api_client.get(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) in {
            PERMISSION_DENIED_TO_VIEW_TASK_MEMBERSHIP,
            "You do not have permission to perform this action.",
        }

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_patch_actor_has_no_permission(
        self, actor_fixture, request, task_membership_read_only, api_client, monkeypatch
    ):
        actor, _ = request.getfixturevalue(actor_fixture)

        data = {"role": "viewer"}
        url = parse_url(BASENAME, "detail", task_membership_read_only.id)

        monkeypatch.setattr(TaskMembershipPolicy, "can_view", lambda a, u: True)

        api_client.force_authenticate(user=actor)
        response = api_client.patch(url, data=data)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) in {
            PERMISSION_DENIED_TO_UPDATE_TASK_MEMBERSHIP,
            "You do not have permission to perform this action.",
        }

    @pytest.mark.parametrize(
        "actor_fixture",
        [
            "member_is_member_read_only",
            "member_is_viewer_read_only",
            "user_is_not_member_read_only",
        ],
    )
    def test_delete_actor_has_no_permission(
        self, actor_fixture, request, task_membership_read_only, api_client, monkeypatch
    ):
        actor, _ = request.getfixturevalue(actor_fixture)

        url = parse_url(BASENAME, "detail", task_membership_read_only.id)

        monkeypatch.setattr(TaskMembershipPolicy, "can_view", lambda a, u: True)

        api_client.force_authenticate(user=actor)
        response = api_client.delete(url)

        assert response.status_code == 403
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) in {
            PERMISSION_DENIED_TO_DELETE_TASK_MEMBERSHIP,
            "You do not have permission to perform this action.",
        }
