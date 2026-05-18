import pytest
from django.urls import reverse
from tests.utils import assert_burst_throttle, assert_sustained_throttle
from tms_auth.api.v1.serializers import JWTRefreshSerializer
from tms_auth.api.v1.throttling import RefreshJwtThrottleBurst, RefreshJwtThrottleSustained

BASENAME = "refresh-jwt"


@pytest.mark.django_db
class TestThrottling:
    def test_read_burst_throttle(self, api_client, monkeypatch):
        monkeypatch.setattr(
            JWTRefreshSerializer, "validate", lambda _, a: {"access": "fake_access"}
        )
        assert_burst_throttle(
            None,
            reverse(BASENAME),
            "post",
            api_client,
            "refresh_jwt",
            2,
            100,
            RefreshJwtThrottleBurst,
            RefreshJwtThrottleSustained,
            data={"refresh": "fake_access"},
        )

    def test_read_sustained_throttle(self, api_client, monkeypatch):
        monkeypatch.setattr(
            JWTRefreshSerializer, "validate", lambda _, a: {"access": "fake_access"}
        )
        assert_sustained_throttle(
            None,
            reverse(BASENAME),
            "post",
            api_client,
            "refresh_jwt",
            100,
            2,
            RefreshJwtThrottleBurst,
            RefreshJwtThrottleSustained,
            data={"refresh": "fake_access"},
        )
