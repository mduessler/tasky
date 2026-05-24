import pytest
from tests.utils import assert_log, build_request
from user.api.v1.serializers import TmsUserReadSerializer


@pytest.mark.django_db
class TestPolicyLogging:
    def test_can_delete_logging(
        self, active_user_read_only, inactive_user_read_only, caplog_loguru
    ):
        serializer = TmsUserReadSerializer(
            instance=inactive_user_read_only,
            context={"request": build_request("get", active_user_read_only)},
        )

        assert serializer.data["can_delete"] is False

        log_record = caplog_loguru.records[-3]
        assert_log(
            log_record,
            "Actor is allowed to delete user:",
            "DEBUG",
            user=inactive_user_read_only.id,
        )

    def test_editable_fields_logging(
        self, superuser_read_only, inactive_user_read_only, caplog_loguru
    ):
        serializer = TmsUserReadSerializer(
            instance=inactive_user_read_only,
            context={"request": build_request("get", superuser_read_only)},
        )

        assert "username" in serializer.data["editable_fields"]

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Actor is allowed to update user:",
            "DEBUG",
            user=inactive_user_read_only.id,
        )
