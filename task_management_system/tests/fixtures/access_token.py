from datetime import timedelta

import pytest
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


@pytest.fixture
def access_token_factory():
    def _factory(user, expired=False):
        token = AccessToken.for_user(user)
        if expired:
            token.set_exp(lifetime=timedelta(seconds=-1))
        return str(token)

    return _factory


@pytest.fixture
def refresh_token_factory():
    def _factory(user, expired=False):
        token = RefreshToken.for_user(user)
        if expired:
            token.set_exp(lifetime=timedelta(seconds=-1))
        return str(token)

    return _factory
