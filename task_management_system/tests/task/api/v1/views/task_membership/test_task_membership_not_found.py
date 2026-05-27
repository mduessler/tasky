from __future__ import annotations

import pytest
from task.errors import TASK_MEMBERSHIP_DOES_NOT_EXIST
from tests.utils import parse_url

BASENAME = "membership"


@pytest.mark.django_db
class TestNotFound:
    @pytest.mark.parametrize("method", ["get", "patch", "delete"])
    def test_detail(self, method, superuser_read_only, api_client):
        data = {"role": "viewer"} if method == "patch" else {}
        url = parse_url(BASENAME, "detail", 9999)

        api_client.force_authenticate(user=superuser_read_only)
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 404
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == TASK_MEMBERSHIP_DOES_NOT_EXIST
