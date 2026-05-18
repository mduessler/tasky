from task_management_system.core.permissions import BasePermission, BasePermissionRole


class DummyPermissionRole(BasePermissionRole):
    ONE = "one"
    TWO = "two"
    THREE = "three"
    FOUR = "four"


class DummyPermission(BasePermission):
    update_permissions = {
        DummyPermissionRole.ONE: {"username", "email", "password", "first_name", "last_name"},
        DummyPermissionRole.TWO: {"first_name", "last_name", "email", "is_superuser"},
        DummyPermissionRole.THREE: set(),
        DummyPermissionRole.FOUR: set(),
    }

    delete_permissions = {
        DummyPermissionRole.ONE: True,
        DummyPermissionRole.TWO: True,
        DummyPermissionRole.THREE: False,
        DummyPermissionRole.FOUR: False,
    }

    create_permissions = {
        DummyPermissionRole.ONE: True,
        DummyPermissionRole.TWO: True,
        DummyPermissionRole.THREE: True,
        DummyPermissionRole.FOUR: True,
    }

    view_permissions = {
        DummyPermissionRole.ONE: True,
        DummyPermissionRole.TWO: True,
        DummyPermissionRole.THREE: True,
        DummyPermissionRole.FOUR: True,
    }
