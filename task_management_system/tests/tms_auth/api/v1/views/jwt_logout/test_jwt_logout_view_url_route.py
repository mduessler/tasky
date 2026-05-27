import pytest
from django.urls import resolve, reverse

BASENAME = "logout-jwt"


@pytest.mark.django_db
class TestUrlroute:
    def test_reverse(self):
        assert "/api/auth/logout/" == reverse(BASENAME)

    def test_resolve(self):
        resolver = resolve("/api/auth/logout/")
        assert resolver.view_name == f"{BASENAME}"
