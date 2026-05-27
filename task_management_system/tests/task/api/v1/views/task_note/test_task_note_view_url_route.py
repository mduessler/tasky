from __future__ import annotations

import pytest
from django.urls import resolve, reverse

BASENAME = "note"


@pytest.mark.django_db
class TestUrlRoute:
    def test_list_reverse(self):
        assert "/api/v1/note/" == reverse(f"{BASENAME}-list")

    def test_list_resolve(self):
        resolver = resolve("/api/v1/note/")
        assert resolver.view_name == f"{BASENAME}-list"

    def test_detail_reverse(self):
        url = reverse(f"{BASENAME}-detail", args=[1])
        assert "/api/v1/note/1/" == url

    def test_detail_resolve(self):
        resolver = resolve("/api/v1/note/1/")
        assert resolver.view_name == f"{BASENAME}-detail"
