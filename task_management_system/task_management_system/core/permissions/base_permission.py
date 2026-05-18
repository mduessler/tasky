from loguru import logger
from task.models import Role

from .base_permission_role import BasePermissionRole


class BasePermission:
    @classmethod
    def get_permission(cls, attr: str, role: BasePermissionRole | Role) -> bool | set[str]:
        try:
            if (permissions := getattr(cls, attr)) is None:
                raise AttributeError(f"Mapping '{attr}' does not exist in {cls.__name__}.")

            return permissions[role]  # type: ignore[no-any-return]
        except KeyError as exc:
            logger.critical(
                f"Security Configuration Error: No {attr} defined for role '{role}' "
                f"in {cls.__name__}. Reason: {exc}."
            )
            raise RuntimeError(f"Role '{role}' is missing in {cls.__name__} mapping.")
        except AttributeError as exc:
            logger.critical(
                f"Security Configuration Error: No {attr} is not defined "
                f"in {cls.__name__}. Reason: {exc}."
            )
            raise RuntimeError(f"Role '{attr}' is missing in {cls.__name__}.")

    @classmethod
    def get_view_permission(cls, role: BasePermissionRole | Role) -> bool:
        return cls.get_permission("view_permissions", role)  # type: ignore[return-value]

    @classmethod
    def get_create_permission(cls, role: BasePermissionRole | Role) -> bool:
        return cls.get_permission("create_permissions", role)  # type: ignore[return-value]

    @classmethod
    def get_delete_permission(cls, role: BasePermissionRole | Role) -> bool:
        return cls.get_permission("delete_permissions", role)  # type: ignore[return-value]

    @classmethod
    def get_update_permission(cls, role: BasePermissionRole | Role) -> set[str]:
        return cls.get_permission("update_permissions", role)  # type: ignore[return-value]
