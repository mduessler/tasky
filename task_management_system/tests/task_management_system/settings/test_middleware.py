from task_management_system.settings import production


class TestMiddleware:
    def test_middleware_order_and_content(self):
        expected = [
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            "task_management_system.core.logging.middleware.RequestContextLogMiddleware",
        ]

        assert expected == production.MIDDLEWARE
