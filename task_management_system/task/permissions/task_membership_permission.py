from task.models import Role

from task_management_system.core.permissions import BasePermission


class TaskMembershipPermissions(BasePermission):  # type: ignore[misc]
    update_permissions = {
        Role.OWNER: {"role"},
        Role.ADMIN: {"role"},
        Role.MEMBER: set(),
        Role.VIEWER: set(),
    }
    delete_permissions = {
        Role.OWNER: True,
        Role.ADMIN: True,
        Role.MEMBER: False,
        Role.VIEWER: False,
    }
    create_permissions = {
        Role.OWNER: True,
        Role.ADMIN: True,
        Role.MEMBER: False,
        Role.VIEWER: False,
    }
    view_permissions = {
        Role.OWNER: True,
        Role.ADMIN: True,
        Role.MEMBER: True,
        Role.VIEWER: True,
    }
