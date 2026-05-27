from __future__ import annotations

import pytest
from django.urls import resolve, reverse

BASENAME = "register-user"


@pytest.mark.django_db
class TestUrlRoute:
    def test_reverse(self):
        assert "/api/auth/register/" == reverse(BASENAME)

    def test_resolve(self):
        resolver = resolve("/api/auth/register/")
        assert resolver.view_name == BASENAME
