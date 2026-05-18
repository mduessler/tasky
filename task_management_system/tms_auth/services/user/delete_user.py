from user.models import TmsUser


def delete_user(user: TmsUser, to_delete: TmsUser) -> None:
    if not user.is_staff:
        raise PermissionError(f"User {user} has not the permission to delete the user.")

    to_delete.delete()
