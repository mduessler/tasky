from datetime import timedelta

import pytest
from django.db import connection
from django.test import utils
from django.utils.timezone import now
from freezegun import freeze_time
from registration.policies import RegistrationPolicy
from tests.utils import assert_log


@pytest.mark.django_db
class TestRegistrationPolicy:
    class TestCanVerifyVerificationToken:
        def test_is_user_is_inactive_true(self, email_token, caplog_loguru):
            result = RegistrationPolicy.can_verify_token(email_token.user, email_token)

            assert result is True

            log_record = caplog_loguru.records[-1]
            assert_log(log_record, "Allowed: Can verify token.", "DEBUG")

        def test_user_is_active_false(self, active_user, email_token, caplog_loguru):
            result = RegistrationPolicy.can_verify_token(active_user, email_token)

            assert result is False

            log_record = caplog_loguru.records[-1]
            assert_log(
                log_record,
                "Permission denied: Can not verify verification token. User is already activated.",
                "WARNING",
            )

        def test_token_is_expired(self, inactive_user, email_token, caplog_loguru):
            with freeze_time(now() + timedelta(minutes=16)):
                result = RegistrationPolicy.can_verify_token(inactive_user, email_token)

                assert result is False

                log_record = caplog_loguru.records[-1]
                assert_log(
                    log_record,
                    "Permission denied: Verification token is expired.",
                    "WARNING",
                )

        def test_email_verification_token_and_user_do_not_match(
            self, active_user, email_token, caplog_loguru
        ):
            active_user.is_active = False
            active_user.save()
            result = RegistrationPolicy.can_verify_token(active_user, email_token)

            assert result is False

            log_record = caplog_loguru.records[-1]
            assert_log(
                log_record,
                "Permission denied: Verification token does not belong to user.",
                "WARNING",
            )

        def test_is_efficient(self, active_user, email_token):
            with utils.CaptureQueriesContext(connection) as queries:
                RegistrationPolicy.can_verify_token(active_user, email_token)

            assert len(queries) <= 1
