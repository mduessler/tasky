import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    client = APIClient()
    client.defaults["CONTENT_TYPE"] = "application/json"
    client.default_format = "json"
    return client


@pytest.fixture
def auth_client():
    def get(user, pw):
        pw = "ThisIsATestingPassword" if not pw else pw
        api_client = APIClient()
        api_client.defaults["CONTENT_TYPE"] = "application/json"
        response = api_client.post(
            reverse("login-jwt"),
            data={
                "email": user.email,
                "password": pw,
            },
        )
        assert response.status_code == 200
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data["access"]}")
        return api_client

    return get


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()
