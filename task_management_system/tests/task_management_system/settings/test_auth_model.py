from task_management_system.settings import production


class TestAuthModel:
    def test_auth_user_model(self):
        expected = "user.TmsUser"
        assert expected == production.AUTH_USER_MODEL
