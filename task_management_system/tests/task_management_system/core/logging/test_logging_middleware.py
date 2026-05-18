from uuid import UUID

import pytest  # noqa F401
from django.http import HttpResponse
from loguru import logger
from tests.utils import assert_log, build_django_request

from task_management_system.core.logging.middleware import RequestContextLogMiddleware


def get_response(_):
    logger.warning("Test logging message.")
    return HttpResponse()


@pytest.mark.django_db
class TestRequestContextLogMiddleware:
    path = "/just/a/path/"

    def test_request_id_is_valid_uuid(self, active_user, caplog_loguru):
        request = build_django_request(method="get", user=active_user, path=self.path)
        middleware = RequestContextLogMiddleware(get_response)
        middleware(request)

        record = caplog_loguru.records[0]

        assert "extra" in record

        request_id = record["extra"]["id"]
        UUID(request_id)

    def test_logging_context(self, active_user, caplog_loguru):
        request = build_django_request(method="get", user=active_user, path=self.path)

        assert caplog_loguru.records == []

        middleware = RequestContextLogMiddleware(get_response)
        middleware(request)

        assert len(caplog_loguru.records) == 1

        record = caplog_loguru.records[0]
        context = {
            "id": record["extra"]["id"],
            "actor": active_user.id,
            "path": self.path,
            "method": "GET",
        }

        assert_log(record, "Test logging message.", "WARNING", **context)

    def test_anonymous_user(self, anonymous_user, caplog_loguru):
        request = build_django_request(method="get", user=anonymous_user, path=self.path)
        middleware = RequestContextLogMiddleware(get_response)
        middleware(request)

        record = caplog_loguru.records[0]
        context = {
            "id": record["extra"]["id"],
            "actor": None,
            "path": self.path,
            "method": "GET",
        }

        assert_log(record, "Test logging message.", "WARNING", **context)

    def test_request_id_is_unique(self, active_user, caplog_loguru):
        request = build_django_request(method="get", user=active_user, path=self.path)
        middleware = RequestContextLogMiddleware(get_response)

        middleware(request)
        record = caplog_loguru.records[-1]
        request_id_1 = record["extra"]["id"]

        middleware(request)
        record = caplog_loguru.records[-1]
        request_id_2 = record["extra"]["id"]

        assert request_id_1 != request_id_2

    def test_middleware_call(self, active_user):
        called = False

        def get_response(_):
            nonlocal called
            called = True
            return HttpResponse()

        request = build_django_request(method="get", user=active_user, path=self.path)
        middleware = RequestContextLogMiddleware(get_response)
        response = middleware(request)

        assert called is True
        assert response.status_code == 200
