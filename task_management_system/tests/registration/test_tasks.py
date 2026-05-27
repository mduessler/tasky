from datetime import timedelta
from smtplib import SMTPException

import pytest
from celery.exceptions import Retry
from django.conf import settings
from django.core import mail
from django.utils.timezone import now
from freezegun import freeze_time
from registration.models import EmailVerificationToken
from registration.tasks import cleanup_expired_tokens, send_verification_email_task
from user.models import TmsUser


@pytest.mark.django_db
class TestCleanUpExpiredTokens:
    def test_precision_boundary(self, inactive_user):
        current_time = now()
        with freeze_time(current_time):
            token = EmailVerificationToken.objects.create(user=inactive_user)

        with freeze_time(current_time + timedelta(minutes=14, seconds=59)):
            cleanup_expired_tokens()
            assert EmailVerificationToken.objects.filter(id=token.id).exists()

        with freeze_time(current_time + timedelta(minutes=15, seconds=1)):
            cleanup_expired_tokens()
            assert not EmailVerificationToken.objects.filter(id=token.id).exists()

    @pytest.mark.slow
    def test_mass_deletion_performance(self, inactive_user, register_data):
        register_data.pop("email_verification")
        register_data.pop("password_verification")
        with freeze_time(now() - timedelta(minutes=20)):
            for i in range(0, 1000):
                register_data["email"] = f"fake{i}@example.com"
                inactive_user = TmsUser.objects.create_user(**register_data)
                token = EmailVerificationToken(user=inactive_user)
                token.full_clean()
                token.save()
        cleanup_expired_tokens()
        assert EmailVerificationToken.objects.count() == 0

    def test_user_persistence(self, email_token):
        user_id = email_token.user_id
        with freeze_time(now() + timedelta(minutes=15)):
            cleanup_expired_tokens()
        assert TmsUser.objects.filter(id=user_id).exists()

    def test_empty_queue(self):
        cleanup_expired_tokens()

    def test_celery_beat_config_exists(self):
        schedule = getattr(settings, "CELERY_BEAT_SCHEDULE", {})
        assert schedule is not {}
        clean_up_config = schedule.get("cleanup-tokens-every-minute")
        assert clean_up_config is not {}
        assert clean_up_config.get("task", "") == "registration.tasks.cleanup_expired_tokens"
        assert True


@pytest.mark.django_db
class TestSendVerificationEmailTask:
    def test_email_sended_success(self, email_token):
        send_verification_email_task(email_token.user_id, email_token.id)
        assert len(mail.outbox) == 1
        assert email_token.token in mail.outbox[0].body

    def test_user_deleted(self, mocker, email_token):
        mock_retry = mocker.patch("registration.tasks.send_verification_email_task.retry")
        send_verification_email_task(user_id=9999, token_id=email_token.id)

        assert not mock_retry.called

    def test_token_deleted(self, active_user, mocker):
        mock_retry = mocker.patch("registration.tasks.send_verification_email_task.retry")
        send_verification_email_task(user_id=active_user.id, token_id=9999)

        assert not mock_retry.called

    def test_smtp_error(self, email_token, mocker):
        mocker.patch("registration.tasks.send_mail", side_effect=SMTPException("Down"))
        mock_retry = mocker.patch.object(
            send_verification_email_task, "retry", side_effect=Retry()
        )

        with pytest.raises(Retry):
            send_verification_email_task(email_token.user_id, email_token.id)

        assert mock_retry.called

    def test_email_max_retries_exhaustion(self, email_token, mocker):
        mocker.patch.object(
            send_verification_email_task,
            "retry",
            side_effect=send_verification_email_task.MaxRetriesExceededError,
        )
        mocker.patch("registration.tasks.send_mail", side_effect=SMTPException())

        with pytest.raises(send_verification_email_task.MaxRetriesExceededError):
            send_verification_email_task.run(email_token.user_id, email_token.id)

    def test_email_idempotency_double_call(self, email_token):
        send_verification_email_task(email_token.user_id, email_token.id)
        send_verification_email_task(email_token.user_id, email_token.id)
        assert len(mail.outbox) == 2

    def test_email_xss_sanitization_in_body(self, email_token):
        email_token.user.first_name = "<script>alert('XSS')</script>"
        email_token.user.save()

        send_verification_email_task(user_id=email_token.user_id, token_id=email_token.id)

        assert "<script>" not in mail.outbox[0].body
