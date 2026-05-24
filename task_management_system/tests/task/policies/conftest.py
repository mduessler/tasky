import pytest


@pytest.fixture(scope="class", autouse=True)
def preload(
    member_is_owner_read_only,
    member_is_admin_read_only,
    member_is_member_read_only,
    member_is_viewer_read_only,
    user_is_not_member_read_only,
    superuser_read_only,
):
    pass
