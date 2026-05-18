from user.permissions import TmsUserPermission


class TestUserPermission:
    class TestUpdate:
        def test_self(self):
            assert TmsUserPermission.get_update_permission("self") == {
                "email",
                "username",
                "first_name",
                "last_name",
                "password",
            }

        def test_superuser(self):
            assert TmsUserPermission.get_update_permission("superuser") == {
                "username",
                "first_name",
                "last_name",
                "is_superuser",
                "is_staff",
            }

        def test_group_member(self):
            assert TmsUserPermission.get_update_permission("group-member") == set()

        def test_other(self):
            assert TmsUserPermission.get_update_permission("other") == set()

    class TestDelete:
        def test_self(self):
            assert TmsUserPermission.get_delete_permission("self") is True

        def test_superuser(self):
            assert TmsUserPermission.get_delete_permission("superuser") is True

        def test_group_member(self):
            assert TmsUserPermission.get_delete_permission("group-member") is False

        def test_other(self):
            assert TmsUserPermission.get_delete_permission("other") is False

    class TestCreate:
        def test_self(self):
            assert TmsUserPermission.get_create_permission("self") is False

        def test_superuser(self):
            assert TmsUserPermission.get_create_permission("superuser") is False

        def test_group_member(self):
            assert TmsUserPermission.get_create_permission("group-member") is False

        def test_other(self):
            assert TmsUserPermission.get_create_permission("other") is False

    class TestView:
        def test_self(self):
            assert TmsUserPermission.get_view_permission("self") is True

        def test_superuser(self):
            assert TmsUserPermission.get_view_permission("superuser") is True

        def test_group_member(self):
            assert TmsUserPermission.get_view_permission("group-member") is True

        def test_other(self):
            assert TmsUserPermission.get_view_permission("other") is False
