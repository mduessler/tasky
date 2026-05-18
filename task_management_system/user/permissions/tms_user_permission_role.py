from task_management_system.core.permissions import BasePermissionRole


class TmsUserPermissionRole(BasePermissionRole):  # type: ignore[misc]
    SELF = "self"
    SUPERUSER = "superuser"
    GROUP_MEMBER = "group-member"
    OTHER = "other"
