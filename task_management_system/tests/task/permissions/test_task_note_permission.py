from task.models import Role
from task.permissions import TaskNotePermissions


class TestTaskNotePermissions:
    class TestUpdate:
        def test_owner(self):
            assert TaskNotePermissions.get_update_permission(Role.OWNER) == {"note"}

        def test_admin(self):
            assert TaskNotePermissions.get_update_permission(Role.ADMIN) == {"note"}

        def test_member(self):
            assert TaskNotePermissions.get_update_permission(Role.MEMBER) == set()

        def test_viewer(self):
            assert TaskNotePermissions.get_update_permission(Role.VIEWER) == set()

    class TestDelete:
        def test_owner(self):
            assert TaskNotePermissions.get_delete_permission(Role.OWNER) is True

        def test_admin(self):
            assert TaskNotePermissions.get_delete_permission(Role.ADMIN) is True

        def test_member(self):
            assert TaskNotePermissions.get_delete_permission(Role.MEMBER) is False

        def test_viewer(self):
            assert TaskNotePermissions.get_delete_permission(Role.VIEWER) is False

    class TestCreate:
        def test_owner(self):
            assert TaskNotePermissions.get_create_permission(Role.OWNER) is True

        def test_admin(self):
            assert TaskNotePermissions.get_create_permission(Role.ADMIN) is True

        def test_member(self):
            assert TaskNotePermissions.get_create_permission(Role.MEMBER) is True

        def test_viewer(self):
            assert TaskNotePermissions.get_create_permission(Role.VIEWER) is False

    class TestView:
        def test_owner(self):
            assert TaskNotePermissions.get_view_permission(Role.OWNER) is True

        def test_admin(self):
            assert TaskNotePermissions.get_view_permission(Role.ADMIN) is True

        def test_member(self):
            assert TaskNotePermissions.get_view_permission(Role.MEMBER) is True

        def test_viewer(self):
            assert TaskNotePermissions.get_view_permission(Role.VIEWER) is True
