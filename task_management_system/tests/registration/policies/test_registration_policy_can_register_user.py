import pytest
from django.db import connection
from django.test import utils
from registration.policies import RegistrationPolicy
from tests.utils import assert_log
from user.models import TmsUser


@pytest.mark.django_db
class TestCanRegisterUser:
    def test_is_true(self, data, caplog_loguru):
        result = RegistrationPolicy.can_register_user(data)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Allowed: Can create an inactive user.", "DEBUG")

    def test_email_already_exists(self, data, caplog_loguru):
        TmsUser.objects.create(**data)
        result = RegistrationPolicy.can_register_user(data)

        assert result is False

        log_record = caplog_loguru.records[-1]
        assert_log(
            log_record,
            "Permission denied: A user with the given email already exists.",
            "WARNING",
        )

    def test_user_with_same_username_exists(self, data, caplog_loguru):
        TmsUser.objects.create(**data)
        data["email"] = "an-other@email.com"
        result = RegistrationPolicy.can_register_user(data)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Allowed: Can create an inactive user.", "DEBUG")

    def test_user_with_same_first_last_name_exists(self, data, caplog_loguru):
        TmsUser.objects.create(**data)
        data["email"] = "an-other@email.com"
        data["username"] = "an-other-username"
        result = RegistrationPolicy.can_register_user(data)

        assert result is True

        log_record = caplog_loguru.records[-1]
        assert_log(log_record, "Allowed: Can create an inactive user.", "DEBUG")

    def test_is_efficient(self, data):
        with utils.CaptureQueriesContext(connection) as queries:
            RegistrationPolicy.can_register_user(data)

        assert len(queries) <= 1
