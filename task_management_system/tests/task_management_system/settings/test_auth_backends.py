from task_management_system.settings import production


class TestAuthenticationBackends:
    def test_auth_backends_list(self):
        expected = ["tms_auth.backends.TmsEmailBackend"]
        assert expected == production.AUTHENTICATION_BACKENDS
