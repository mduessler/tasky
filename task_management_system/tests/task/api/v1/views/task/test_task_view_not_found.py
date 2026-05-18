from __future__ import annotations

import pytest
from task.errors import TASK_DOES_NOT_EXIST
from tests.task.api.v1.views.utils import select_data_dict
from tests.utils import parse_url

BASENAME = "task"


@pytest.mark.django_db
class TestNotFound:
    @pytest.mark.parametrize(
        "method, url_name",
        [
            ("get", "detail"),
            ("patch", "detail"),
            ("delete", "detail"),
            ("get", "memberships"),
            ("post", "membership"),
            ("get", "notes"),
            ("post", "note"),
        ],
    )
    def test_detail(
        self,
        method,
        url_name,
        superuser,
        api_client,
        data_task,
        data_task_membership,
        data_task_note_author_is_member,
    ):
        data = select_data_dict(
            method, url_name, data_task, data_task_membership, data_task_note_author_is_member
        )
        url = parse_url(BASENAME, url_name, 9999)

        api_client.force_authenticate(user=superuser)
        response = getattr(api_client, method)(url, data=data)

        assert response.status_code == 404
        assert set(response.data.keys()) == {"detail"}
        assert str(response.data["detail"]) == TASK_DOES_NOT_EXIST
