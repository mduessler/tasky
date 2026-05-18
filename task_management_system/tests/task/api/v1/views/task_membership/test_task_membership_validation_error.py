from __future__ import annotations

import pytest
from tests.utils import parse_url

BASENAME = "membership"


@pytest.mark.django_db
class TestValidationError:
    def test_patch(self, member_is_owner, task_membership, api_client):
        actor, _ = member_is_owner
        old_role = task_membership.role

        data = {"role": ""}
        url = parse_url(BASENAME, "detail", task_membership.id)

        api_client.force_authenticate(user=actor)
        response = api_client.patch(url, data=data)

        task_membership.refresh_from_db()
        assert response.status_code == 400
        assert task_membership.role == old_role
