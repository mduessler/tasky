import pytest
from loguru import logger

from task_management_system.core.logging import bind_context_dict, request_context


@pytest.fixture(autouse=True)
def clear_logging_context():
    token = request_context.set(None)
    yield
    request_context.reset(token)


class TestBindContextDict:
    def test_bind_context_dict_adds_context(self, caplog_loguru):
        bind_context_dict(user=1, task=99)
        logger.info("test message")

        assert len(caplog_loguru.records) == 1

        record = caplog_loguru.records[-1]
        assert record["extra"] == {"user": 1, "task": 99}

    def test_bind_context_dict_empty_kwargs(self, caplog_loguru):
        bind_context_dict()
        logger.info("empty test")

        record = caplog_loguru.records[-1]
        assert "task" not in record["extra"]
        assert record["extra"] == {}

    def test_bind_context_dict_extra_is_updated(self, caplog_loguru):
        bind_context_dict(user=1, task=99)
        logger.info("test message")

        record = caplog_loguru.records[-1]
        assert record["extra"] == {"user": 1, "task": 99}

        bind_context_dict(note=2)
        logger.info("next messsage")

        record = caplog_loguru.records[-1]
        assert record["extra"] == {"user": 1, "task": 99, "note": 2}

    def test_bind_context_dict_updates_between_calls(self, caplog_loguru):
        bind_context_dict(task=1)
        logger.info("first")
        _ = caplog_loguru.records[-1]

        bind_context_dict(task=2)
        logger.info("second")
        rec2 = caplog_loguru.records[-1]

        assert rec2["extra"]["task"] == 2

    def test_bind_context_dict_does_not_mutate_input(self, caplog_loguru):
        data = {"task": 1}
        bind_context_dict(**data)
        data["task"] = 999
        logger.info("mutation test")

        record = caplog_loguru.records[-1]
        assert record["extra"]["task"] == 1

    def test_patcher_handles_none_context(self, caplog_loguru):
        token = request_context.set(None)

        try:
            logger.info("Test log without context")
        finally:
            request_context.reset(token)

        assert len(caplog_loguru.records) == 1
        record = caplog_loguru.records[0]
        assert "id" not in record["extra"]

    def test_patcher_integrates_context_correctly(self, caplog_loguru):
        test_data = {"id": "first-request", "actor": 1}
        token = request_context.set(test_data)

        try:
            logger.info("Test log with context")
        finally:
            request_context.reset(token)

        record = caplog_loguru.records[-1]
        assert record["extra"]["id"] == "first-request"
        assert record["extra"]["actor"] == 1
