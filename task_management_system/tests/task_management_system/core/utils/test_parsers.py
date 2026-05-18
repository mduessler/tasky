import pytest
from rest_framework.exceptions import ParseError
from tests.utils import assert_log, build_request

from task_management_system.core.utils.parsers import get_int_query_param


@pytest.mark.django_db
class TestGetIntQueryParam:
    def test_success(self, active_user, caplog_loguru):
        request = build_request(
            method="get", user=active_user, path="/just/", query_params={"user": 5, "task": 2}
        )

        result = get_int_query_param(request, "user")

        assert isinstance(result, int)
        assert result == 5

        record = caplog_loguru.records[-1]
        assert_log(record, "Converted 5 to integer.", "DEBUG")

        result = get_int_query_param(request, "task")

        assert isinstance(result, int)
        assert result == 2

        record = caplog_loguru.records[-1]
        assert_log(record, "Converted 2 to integer.", "DEBUG")

    def test_query_parmeter_does_not_exists(self, active_user, caplog_loguru):
        request = build_request(
            method="get", user=active_user, path="/just/", query_params={"user": 5, "task": 2}
        )
        result = get_int_query_param(request, "membership")

        assert result is None

        record = caplog_loguru.records[-1]
        assert_log(record, "Invalid query parameter: membership.", "WARNING")

    def test_no_query_parameter(self, active_user, caplog_loguru):
        request = build_request(method="get", user=active_user, path="/just/")
        result = get_int_query_param(request, "membership")

        assert result is None

        record = caplog_loguru.records[-1]
        assert_log(record, "Invalid query parameter: membership.", "WARNING")

    def test_key_error(self, active_user, caplog_loguru):
        request = build_request(
            method="get", user=active_user, path="/just/", query_params={"user": "--"}
        )

        with pytest.raises(ParseError) as exc:
            get_int_query_param(request, "user")
        assert str(exc.value) == "invalid literal for int() with base 10: '--'"

        record = caplog_loguru.records[0]
        assert_log(record, "Invalid value: --.", "WARNING")
