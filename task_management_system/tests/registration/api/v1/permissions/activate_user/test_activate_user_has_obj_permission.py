import pytest
from registration.api.v1.permissions import ActivateUserPermission
from tests.utils import DummyView, assert_log, build_request


@pytest.mark.django_db
class TestActivateUserPermission:
    class TestHasObjPermission:
        @pytest.mark.parametrize("method", ["delete", "get", "patch", "post", "put"])
        def test_not_allowed(self, method, anonymous_user, caplog_loguru):
            req = build_request(method, anonymous_user)
            result = ActivateUserPermission().has_object_permission(req, DummyView(), object())

            assert result is False

            log_record = caplog_loguru.records[-1]
            assert_log(
                log_record,
                "Permission denied: This operation is not allowed in the registration views.",
                "WARNING",
            )
