import pytest
from django.urls import resolve, reverse

BASENAME = "refresh-jwt"


@pytest.mark.django_db
class TestUrlroute:
    def test_reverse(self):
        assert "/api/auth/refresh/" == reverse(BASENAME)

    def test_resolve(self):
        resolver = resolve("/api/auth/refresh/")
        assert resolver.view_name == f"{BASENAME}"
