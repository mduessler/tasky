import pytest
from loguru import logger


@pytest.fixture
def caplog_loguru():
    class LogSink:
        def __init__(self):
            self.records = []

        def __call__(self, message):
            self.records.append(message.record)

    sink = LogSink()
    handler_id = logger.add(sink, format="{message}")
    yield sink
    logger.remove(handler_id)
