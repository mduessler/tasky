from task_management_system.settings import production


class TestRestFramework:
    @property
    def rf_settings(self):
        return production.REST_FRAMEWORK

    def test_authentication_classes(self):
        expected = ("rest_framework_simplejwt.authentication.JWTAuthentication",)
        assert self.rf_settings["DEFAULT_AUTHENTICATION_CLASSES"] == expected

    def test_permission_classes(self):
        expected = ["rest_framework.permissions.IsAuthenticated"]
        assert self.rf_settings["DEFAULT_PERMISSION_CLASSES"] == expected

    def test_exception_handler(self):
        expected = "task_management_system.core.exceptions.custom_exception_handler"
        assert self.rf_settings["EXCEPTION_HANDLER"] == expected

    def test_versioning_class(self):
        expected = "rest_framework.versioning.URLPathVersioning"
        assert self.rf_settings["DEFAULT_VERSIONING_CLASS"] == expected

    def test_default_version(self):
        assert self.rf_settings["DEFAULT_VERSION"] == "v1"

    def test_allowed_versions(self):
        assert self.rf_settings["ALLOWED_VERSIONS"] == ["v1"]

    def test_schema_class(self):
        expected = "drf_spectacular.openapi.AutoSchema"
        assert self.rf_settings["DEFAULT_SCHEMA_CLASS"] == expected

    def test_media_type(self):
        assert self.rf_settings["DEFAULT_PARSER_CLASSES"] == ["rest_framework.parsers.JSONParser"]

    def test_throttle_rates_integrity(self):

        ACTIVATE_USER_THROTTLE = {"activate": "5/min", "register": "4/min"}

        TMS_AUTH_THROTTLE = {
            "login_jwt": {"burst": "3/min", "sustained": "200/day"},
            "refresh_jwt": {"burst": "6/hour", "sustained": "144/day"},
            "logout_jwt": {"burst": "3/min", "sustained": "200/day"},
        }

        TMS_USER_THROTTLE = {
            "read": {"burst": "5/sec", "sustained": "2000/day"},
            "create": {"burst": "0/sec", "sustained": "0/day"},
            "delete": {"burst": "1/sec", "sustained": "100/day"},
            "update": {"burst": "2/sec", "sustained": "500/day"},
        }

        TASK_THROTTLE = {
            "read": {"burst": "10/sec", "sustained": "5000/day"},
            "create": {"burst": "2/sec", "sustained": "200/day"},
            "delete": {"burst": "1/sec", "sustained": "50/day"},
            "update": {"burst": "4/sec", "sustained": "1000/day"},
        }
        TASK_MEMBERSHIP = {
            "read": {"burst": "50/sec", "sustained": "5000/day"},
            "create": {"burst": "4/sec", "sustained": "400/day"},
            "delete": {"burst": "1/sec", "sustained": "200/day"},
            "update": {"burst": "4/sec", "sustained": "400/day"},
        }
        TASK_NOTE = {
            "read": {"burst": "100/sec", "sustained": "10000/day"},
            "create": {"burst": "2/sec", "sustained": "800/day"},
            "delete": {"burst": "4/sec", "sustained": "400/day"},
            "update": {"burst": "2/sec", "sustained": "800/day"},
        }

        expected_throttles = {
            "anon": "100/day",
            "user": "1000/day",
            "login_jwt_burst": TMS_AUTH_THROTTLE["login_jwt"]["burst"],
            "login_jwt_sustained": TMS_AUTH_THROTTLE["login_jwt"]["sustained"],
            "refresh_jwt_burst": TMS_AUTH_THROTTLE["refresh_jwt"]["burst"],
            "refresh_jwt_sustained": TMS_AUTH_THROTTLE["refresh_jwt"]["sustained"],
            "logout_jwt_burst": TMS_AUTH_THROTTLE["logout_jwt"]["burst"],
            "logout_jwt_sustained": TMS_AUTH_THROTTLE["logout_jwt"]["sustained"],
            "activate_user": ACTIVATE_USER_THROTTLE["activate"],
            "register_user": ACTIVATE_USER_THROTTLE["register"],
            "tms_user_read_burst": TMS_USER_THROTTLE["read"]["burst"],
            "tms_user_read_sustained": TMS_USER_THROTTLE["read"]["sustained"],
            "tms_user_create_burst": TMS_USER_THROTTLE["create"]["burst"],
            "tms_user_create_sustained": TMS_USER_THROTTLE["create"]["sustained"],
            "tms_user_delete_burst": TMS_USER_THROTTLE["delete"]["burst"],
            "tms_user_delete_sustained": TMS_USER_THROTTLE["delete"]["sustained"],
            "tms_user_update_burst": TMS_USER_THROTTLE["update"]["burst"],
            "tms_user_update_sustained": TMS_USER_THROTTLE["update"]["sustained"],
            "task_read_burst": TASK_THROTTLE["read"]["burst"],
            "task_read_sustained": TASK_THROTTLE["read"]["sustained"],
            "task_create_burst": TASK_THROTTLE["create"]["burst"],
            "task_create_sustained": TASK_THROTTLE["create"]["sustained"],
            "task_delete_burst": TASK_THROTTLE["delete"]["burst"],
            "task_delete_sustained": TASK_THROTTLE["delete"]["sustained"],
            "task_update_burst": TASK_THROTTLE["update"]["burst"],
            "task_update_sustained": TASK_THROTTLE["update"]["sustained"],
            "task_membership_read_burst": TASK_MEMBERSHIP["read"]["burst"],
            "task_membership_read_sustained": TASK_MEMBERSHIP["read"]["sustained"],
            "task_membership_create_burst": TASK_MEMBERSHIP["create"]["burst"],
            "task_membership_create_sustained": TASK_MEMBERSHIP["create"]["sustained"],
            "task_membership_delete_burst": TASK_MEMBERSHIP["delete"]["burst"],
            "task_membership_delete_sustained": TASK_MEMBERSHIP["delete"]["sustained"],
            "task_membership_update_burst": TASK_MEMBERSHIP["update"]["burst"],
            "task_membership_update_sustained": TASK_MEMBERSHIP["update"]["sustained"],
            "task_note_read_burst": TASK_NOTE["read"]["burst"],
            "task_note_read_sustained": TASK_NOTE["read"]["sustained"],
            "task_note_create_burst": TASK_NOTE["create"]["burst"],
            "task_note_create_sustained": TASK_NOTE["create"]["sustained"],
            "task_note_delete_burst": TASK_NOTE["delete"]["burst"],
            "task_note_delete_sustained": TASK_NOTE["delete"]["sustained"],
            "task_note_update_burst": TASK_NOTE["update"]["burst"],
            "task_note_update_sustained": TASK_NOTE["update"]["sustained"],
        }
        actual_throttles = self.rf_settings["DEFAULT_THROTTLE_RATES"]

        assert actual_throttles == expected_throttles
