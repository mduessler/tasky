from task_management_system.settings import production


class TestInstalledApps:
    def test_installed_apps_list(self):
        expected = [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "django.contrib.sites",
            "rest_framework",
            "rest_framework_simplejwt.token_blacklist",
            "drf_spectacular",
            "django_celery_beat",
            "user",
            "tms_auth",
            "registration",
            "task",
        ]

        assert expected == production.INSTALLED_APPS
