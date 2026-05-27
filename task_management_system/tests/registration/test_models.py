from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.timezone import now
from freezegun import freeze_time
from registration.models import EmailVerificationToken


@pytest.mark.django_db
class TestEmailVerification:
    def test_create_token(self, monkeypatch, inactive_user):
        def fake_token(_):
            return 1

        cnt = EmailVerificationToken.objects.count()
        assert cnt == 0

        monkeypatch.setattr("registration.models.randbelow", fake_token)

        token = EmailVerificationToken(user=inactive_user)
        token.full_clean()
        token.save()

        assert token.token == "".join(str(fake_token(_)) for _ in range(6))
        assert inactive_user.id == token.user.id
        assert token.expires_at > now() + timedelta(minutes=14)
        assert token.expires_at < now() + timedelta(minutes=15)
        assert EmailVerificationToken.objects.count() == cnt + 1

    def test_clean(self, active_user):
        with pytest.raises(ValidationError):
            token = EmailVerificationToken(user=active_user)
            token.full_clean()
            token.save()

    def test_email_verification_token_is_expired(self, inactive_user):
        with freeze_time(now()) as frozen_time:
            token = EmailVerificationToken.objects.create(user=inactive_user)
            token.full_clean()

            assert not token.is_expired()

            frozen_time.tick(delta=timedelta(minutes=15, seconds=1))
            token.refresh_from_db()

            assert token.is_expired()

    def test_token_is_immutable(self, inactive_user):
        token = EmailVerificationToken.objects.create(user=inactive_user)

        with pytest.raises(ValidationError):
            token.save()

    def test_one_token_per_user(self, inactive_user):
        EmailVerificationToken.objects.create(user=inactive_user)

        with pytest.raises(IntegrityError):
            EmailVerificationToken.objects.create(user=inactive_user)

    def test_generate_token_not_overwritten(self, inactive_user):
        token = EmailVerificationToken(user=inactive_user, token="123456")
        token.save()

        assert token.token == "123456"

    def test_expires_at_is_set(self, inactive_user):
        token = EmailVerificationToken.objects.create(user=inactive_user)
        assert token.expires_at is not None

    def test_expires_at_precision(self, inactive_user):
        token = EmailVerificationToken.objects.create(user=inactive_user)
        expected = now() + timedelta(minutes=15)
        delta = abs((token.expires_at - expected).total_seconds())

        assert delta < 2
