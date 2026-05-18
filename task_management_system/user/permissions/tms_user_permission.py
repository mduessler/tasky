from task_management_system.core.permissions import BasePermission

from .tms_user_permission_role import TmsUserPermissionRole


class TmsUserPermission(BasePermission):  # type: ignore[misc]
    update_permissions = {
        TmsUserPermissionRole.SELF: {"email", "username", "first_name", "last_name", "password"},
        TmsUserPermissionRole.SUPERUSER: {
            "username",
            "first_name",
            "last_name",
            "is_superuser",
            "is_staff",
        },
        TmsUserPermissionRole.GROUP_MEMBER: set(),
        TmsUserPermissionRole.OTHER: set(),
    }
    delete_permissions = {
        TmsUserPermissionRole.SELF: True,
        TmsUserPermissionRole.SUPERUSER: True,
        TmsUserPermissionRole.GROUP_MEMBER: False,
        TmsUserPermissionRole.OTHER: False,
    }
    create_permissions = {
        TmsUserPermissionRole.SELF: False,
        TmsUserPermissionRole.SUPERUSER: False,
        TmsUserPermissionRole.GROUP_MEMBER: False,
        TmsUserPermissionRole.OTHER: False,
    }
    view_permissions = {
        TmsUserPermissionRole.SELF: True,
        TmsUserPermissionRole.SUPERUSER: True,
        TmsUserPermissionRole.GROUP_MEMBER: True,
        TmsUserPermissionRole.OTHER: False,
    }
