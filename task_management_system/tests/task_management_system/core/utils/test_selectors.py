import pytest
from django.core.exceptions import MultipleObjectsReturned
from django.db import connection
from django.test import utils
from rest_framework.exceptions import NotFound
from tests.utils import assert_log
from tms_auth.errors import USER_DOES_NOT_EXIST
from user.models import TmsUser

from task_management_system.core.utils import get_user


@pytest.mark.django_db
class TestGetUser:
    def test_success(self, active_user, caplog_loguru):
        result = get_user(active_user.id)

        assert isinstance(result, TmsUser)
        assert result.id == active_user.id

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Found: User exists.", "DEBUG")

    def test_not_found(self, caplog_loguru):
        non_existent_id = 9999

        with pytest.raises(NotFound) as exc:
            get_user(non_existent_id)

        assert USER_DOES_NOT_EXIST == str(exc.value.detail)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Not found: User not found. Reaseon TmsUser matching query does not exist..",
            "WARNING",
        )

    def test_multiple_objects_returned(self, monkeypatch, caplog_loguru):
        def mock_get(*args, **kwargs):
            raise MultipleObjectsReturned("Multiple users found")

        monkeypatch.setattr(TmsUser.objects, "get", mock_get)

        with pytest.raises(MultipleObjectsReturned) as exc:
            get_user(1)

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            f"Critical: Multiple Users returned! Reason {exc.value}.",
            "CRITICAL",
        )

    def test_is_efficient(self, active_user):
        with utils.CaptureQueriesContext(connection) as queries:
            get_user(active_user.id)

        assert len(queries) <= 1
