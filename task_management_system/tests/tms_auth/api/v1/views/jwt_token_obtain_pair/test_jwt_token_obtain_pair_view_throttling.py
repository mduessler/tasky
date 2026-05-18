import pytest
from django.urls import reverse
from tests.utils import assert_burst_throttle, assert_sustained_throttle
from tms_auth.api.v1.throttling import LoginJwtThrottleBurst, LoginJwtThrottleSustained

BASENAME = "login-jwt"


@pytest.mark.django_db
class TestThrottling:
    def test_read_burst_throttle(self, superuser, superuser_data, api_client):
        assert_burst_throttle(
            None,
            reverse(BASENAME),
            "post",
            api_client,
            "login_jwt",
            2,
            100,
            LoginJwtThrottleBurst,
            LoginJwtThrottleSustained,
            data={"email": superuser.email, "password": superuser_data["password"]},
        )

    def test_read_sustained_throttle(self, superuser, superuser_data, api_client):
        assert_sustained_throttle(
            None,
            reverse(BASENAME),
            "post",
            api_client,
            "login_jwt",
            100,
            2,
            LoginJwtThrottleBurst,
            LoginJwtThrottleSustained,
            data={"email": superuser.email, "password": superuser_data["password"]},
        )
