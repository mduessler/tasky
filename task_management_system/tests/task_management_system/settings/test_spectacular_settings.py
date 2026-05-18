from task_management_system.settings import production


class TestMiddleware:
    def test_middleware_order_and_content(self):
        expected = {
            "TITLE": "Tasky API",
            "DESCRIPTION": "A collaborative task management REST API with JWT authentication.",
            "VERSION": "1.0.0",
            "SERVE_INCLUDE_SCHEMA": False,
            "COMPONENT_SPLIT_REQUEST": True,
            "SCHEMA_PATH_PREFIX": "/api/v1/",
        }

        assert expected == production.SPECTACULAR_SETTINGS
