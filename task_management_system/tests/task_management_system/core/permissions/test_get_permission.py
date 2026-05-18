import pytest
from tests.task_management_system.core.permissions.utils import (
    DummyPermission,
    DummyPermissionRole,
)


class TestBasePermission:

    def test_returns_bool_permission(self):
        result = DummyPermission.get_permission("view_permissions", DummyPermissionRole.ONE)

        assert result is True

    def test_returns_set_permission(self):
        result = DummyPermission.get_permission("update_permissions", DummyPermissionRole.ONE)

        assert result == {"username", "email", "password", "first_name", "last_name"}

    def test_raises_runtime_error_for_missing_role(self):
        with pytest.raises(RuntimeError):
            DummyPermission.get_permission("view_permissions", "invalid-role")

    def test_logs_critical_for_missing_role(self, mocker):
        logger_mock = mocker.patch(
            "task_management_system.core.permissions.base_permission.logger.critical"
        )

        with pytest.raises(RuntimeError):
            DummyPermission.get_permission("view_permissions", "invalid-role")

        logger_mock.assert_called_once()

    def test_raises_runtime_error_for_missing_mapping(self):
        with pytest.raises(RuntimeError):
            DummyPermission.get_permission("invalid_permissions", DummyPermissionRole.ONE)

    def test_logs_critical_for_missing_mapping(self, mocker):
        logger_mock = mocker.patch(
            "task_management_system.core.permissions.base_permission.logger.critical"
        )

        with pytest.raises(RuntimeError):
            DummyPermission.get_permission("invalid_permissions", DummyPermissionRole.ONE)

        logger_mock.assert_called_once()

    def test_raises_runtime_error_for_empty_mapping(self):
        with pytest.raises(RuntimeError):
            DummyPermission.get_permission("none_permissions", DummyPermissionRole.ONE)

    def test_returns_false_permission(self):
        result = DummyPermission.get_permission("delete_permissions", DummyPermissionRole.THREE)

        assert result is False

    def test_returns_empty_set_permission(self):
        result = DummyPermission.get_permission("update_permissions", DummyPermissionRole.THREE)

        assert result == set()

    def test_returns_create_permission(self):
        result = DummyPermission.get_permission("create_permissions", DummyPermissionRole.TWO)

        assert result is True

    def test_returns_exact_set_without_modification(self):
        result = DummyPermission.get_permission("update_permissions", DummyPermissionRole.TWO)

        assert result == {"first_name", "last_name", "email", "is_superuser"}

    def test_does_not_return_none_for_missing_role(self):
        with pytest.raises(RuntimeError):
            result = DummyPermission.get_permission("view_permissions", "invalid-role")

            assert result is not None

    def test_does_not_return_none_for_missing_mapping(self):
        with pytest.raises(RuntimeError):
            result = DummyPermission.get_permission("invalid_permissions", DummyPermissionRole.ONE)

            assert result is not None
