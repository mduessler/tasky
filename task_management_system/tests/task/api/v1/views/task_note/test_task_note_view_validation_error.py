from __future__ import annotations

import pytest
from tests.utils import parse_url

BASENAME = "note"


@pytest.mark.django_db
class TestValidationError:
    def test_patch(self, member_is_owner, task_note, api_client):
        actor, _ = member_is_owner
        old_note = task_note.note
        data = {"note": ""}
        url = parse_url(BASENAME, "detail", task_note.id)

        api_client.force_authenticate(user=actor)
        response = api_client.patch(url, data=data)

        task_note.refresh_from_db()

        assert response.status_code == 400
        assert task_note.note == old_note
