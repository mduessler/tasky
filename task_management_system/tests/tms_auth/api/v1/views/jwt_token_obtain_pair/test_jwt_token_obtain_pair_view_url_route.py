import pytest
from django.urls import resolve, reverse

BASENAME = "login-jwt"


@pytest.mark.django_db
class TestUrlroute:
    def test_reverse(self):
        assert "/api/auth/login/" == reverse(BASENAME)

    def test_resolve(self):
        resolver = resolve("/api/auth/login/")
        assert resolver.view_name == f"{BASENAME}"
