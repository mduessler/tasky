import pytest
from django.urls import resolve, reverse

BASENAME = "task"


@pytest.mark.django_db
class TestUrlRoute:
    def test_list_reverse(self):
        assert "/api/v1/task/" == reverse(f"{BASENAME}-list")

    def test_list_resolve(self):
        resolver = resolve("/api/v1/task/")
        assert resolver.view_name == f"{BASENAME}-list"

    def test_detail_reverse(self):
        url = reverse(f"{BASENAME}-detail", args=[1])
        assert "/api/v1/task/1/" == url

    def test_detail_resolve(self):
        resolver = resolve("/api/v1/task/1/")
        assert resolver.view_name == f"{BASENAME}-detail"

    def test_memberships_reverse(self):
        url = reverse(f"{BASENAME}-memberships", args=[1])
        assert "/api/v1/task/1/memberships/" == url

    def test_memberships_resolve(self):
        resolver = resolve("/api/v1/task/1/memberships/")
        assert resolver.view_name == f"{BASENAME}-memberships"

    def test_membership_reverse(self):
        url = reverse(f"{BASENAME}-membership", args=[1])
        assert "/api/v1/task/1/membership/" == url

    def test_membership_resolve(self):
        resolver = resolve("/api/v1/task/1/membership/")
        assert resolver.view_name == f"{BASENAME}-membership"

    def test_notes_reverse(self):
        url = reverse(f"{BASENAME}-notes", args=[1])
        assert "/api/v1/task/1/notes/" == url

    def test_notes_resolve(self):
        resolver = resolve("/api/v1/task/1/notes/")
        assert resolver.view_name == f"{BASENAME}-notes"

    def test_note_reverse(self):
        url = reverse(f"{BASENAME}-note", args=[1])
        assert "/api/v1/task/1/note/" == url

    def test_note_resolve(self):
        resolver = resolve("/api/v1/task/1/note/")
        assert resolver.view_name == f"{BASENAME}-note"
