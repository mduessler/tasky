from __future__ import annotations

import pytest
from task.errors import CAN_NOT_REOPEN_COMPLETE_TASK
from tests.utils import parse_url

BASENAME = "task"


@pytest.mark.django_db
class TestValidationError:
    def test_patch(self, member_is_owner_read_only, task_read_only, api_client):
        actor, _ = member_is_owner_read_only
        old_title = task_read_only.title
        url = parse_url(BASENAME, "detail", task_read_only.id)

        api_client.force_authenticate(user=actor)
        response = api_client.patch(
            url,
            data={"title": ""},
        )

        task_read_only.refresh_from_db()

        assert response.status_code == 400
        assert task_read_only.title == old_title

    def test_patch_can_not_reopen_done_task(
        self, member_is_owner_read_only, task_read_only, api_client
    ):
        actor, _ = member_is_owner_read_only
        task_read_only.status = "done"
        task_read_only.save(update_fields=["status"])
        url = parse_url(BASENAME, "detail", task_read_only.id)

        api_client.force_authenticate(user=actor)
        response = api_client.patch(url, data={"status": "todo"})

        task_read_only.refresh_from_db()

        assert response.status_code == 400
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == CAN_NOT_REOPEN_COMPLETE_TASK

    def test_post(self, superuser_read_only, api_client):
        url = parse_url(BASENAME, "list")

        api_client.force_authenticate(user=superuser_read_only)
        response = api_client.post(
            url, data={"title": "", "description": "description", "status": "todo"}
        )

        assert response.status_code == 400

    def test_membership_post(self, member_is_owner_read_only, task_read_only, api_client):
        actor, _ = member_is_owner_read_only
        url = parse_url(BASENAME, "membership", task_read_only.id)

        api_client.force_authenticate(user=actor)
        response = api_client.post(url, data={"role": "viewer"})

        assert response.status_code == 400

    def test_note_post(self, member_is_owner_read_only, task_read_only, api_client):
        actor, _ = member_is_owner_read_only
        url = parse_url(BASENAME, "note", task_read_only.id)

        api_client.force_authenticate(user=actor)
        response = api_client.post(url, data={"note": ""})

        assert response.status_code == 400
