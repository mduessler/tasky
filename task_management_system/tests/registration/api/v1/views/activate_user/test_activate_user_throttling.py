from __future__ import annotations

import pytest
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from registration.api.v1.serializers import ActivateWriteSerializer
from registration.api.v1.throttling import ActivateUserThrottle

BASENAME = "activate-user"


@pytest.mark.django_db
class TestThrottling:
    def test_activate_user_throttle(self, email_token, api_client, monkeypatch):
        data = {"email": email_token.user.email, "token": email_token.token}

        monkeypatch.setattr(ActivateWriteSerializer, "save", lambda s: email_token.user)

        with override_settings(
            REST_FRAMEWORK={
                **settings.REST_FRAMEWORK,
                "DEFAULT_THROTTLE_RATES": {"activate_user": "2/day"},
            }
        ):
            setattr(ActivateUserThrottle, "rate", "2/day")

            for _ in range(2):
                response = api_client.post(reverse(BASENAME), data=data)
                assert response.status_code in {200, 201, 202, 204}

            response = api_client.post(reverse(BASENAME), data=data)
        assert response.status_code == 429
