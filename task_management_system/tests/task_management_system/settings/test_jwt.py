from datetime import timedelta
from os import environ

from task_management_system.settings import production


class TestSimpleJwt:
    def test_jwt_config(self):
        excpected = {
            "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
            "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
            "ROTATE_REFRESH_TOKENS": True,
            "BLACKLIST_AFTER_ROTATION": True,
            "UPDATE_LAST_LOGIN": True,
            "SIGNING_KEY": environ.get("JWT_SECRET_KEY"),
            "ALGORITHM": "HS256",
            "AUTH_HEADER_TYPES": ("Bearer",),
        }
        assert excpected == production.SIMPLE_JWT
