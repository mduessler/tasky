import pytest
from django.urls import reverse
from tests.utils import assert_burst_throttle, assert_sustained_throttle
from tms_auth.api.v1.serializers import JWTLogoutSerializer
from tms_auth.api.v1.throttling import LogoutJwtThrottleBurst, LogoutJwtThrottleSustained

BASENAME = "logout-jwt"


@pytest.mark.django_db
class TestThrottling:
    def test_logout_burst_throttle(
        self, api_client, active_user, access_token_factory, monkeypatch
    ):
        access = access_token_factory(active_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        monkeypatch.setattr(JWTLogoutSerializer, "validate", lambda _, a: {})

        assert_burst_throttle(
            None,
            reverse(BASENAME),
            "post",
            api_client,
            "logout_jwt",
            2,
            100,
            LogoutJwtThrottleBurst,
            LogoutJwtThrottleSustained,
            data={"refresh": "fake_refresh_token"},
        )

    def test_logout_sustained_throttle(
        self, api_client, active_user, access_token_factory, monkeypatch
    ):
        access = access_token_factory(active_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        monkeypatch.setattr(JWTLogoutSerializer, "validate", lambda _, a: {})

        assert_sustained_throttle(
            None,
            reverse(BASENAME),
            "post",
            api_client,
            "logout_jwt",
            100,
            2,
            LogoutJwtThrottleBurst,
            LogoutJwtThrottleSustained,
            data={"refresh": "fake_refresh_token"},
        )
