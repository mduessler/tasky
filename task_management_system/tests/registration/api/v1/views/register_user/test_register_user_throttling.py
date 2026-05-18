from __future__ import annotations

import pytest
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from registration.api.v1.serializers import RegisterWriteSerializer
from registration.api.v1.throttling import RegisterUserThrottle

BASENAME = "register-user"


@pytest.mark.django_db
class TestThrottling:
    def test_register_user_throttle(self, register_data, inactive_user, api_client, monkeypatch):
        monkeypatch.setattr(RegisterWriteSerializer, "is_valid", lambda s, raise_exception: True)
        monkeypatch.setattr(RegisterWriteSerializer, "save", lambda s: inactive_user)

        with override_settings(
            REST_FRAMEWORK={
                **settings.REST_FRAMEWORK,
                "DEFAULT_THROTTLE_RATES": {"register_user": "2/day"},
            }
        ):
            setattr(RegisterUserThrottle, "rate", "2/day")

            for _ in range(2):
                response = api_client.post(reverse(BASENAME), data=register_data)
                assert response.status_code == 201

            response = api_client.post(reverse(BASENAME), data=register_data)
        assert response.status_code == 429
