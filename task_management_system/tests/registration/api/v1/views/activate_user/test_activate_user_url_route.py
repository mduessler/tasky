from __future__ import annotations

import pytest
from django.urls import resolve, reverse

BASENAME = "activate-user"


@pytest.mark.django_db
class TestUrlRoute:
    def test_reverse(self):
        assert "/api/auth/activate/" == reverse(BASENAME)

    def test_resolve(self):
        resolver = resolve("/api/auth/activate/")
        assert resolver.view_name == BASENAME
