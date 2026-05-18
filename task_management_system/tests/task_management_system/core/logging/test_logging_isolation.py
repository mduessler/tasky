import time
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from task_management_system.core.logging.utils import bind_context_dict, request_context


class TestLoggingIsolation:
    def test_concurrent_request_isolation(self, caplog_loguru):
        num_threads = 20

        def worker(thread_id):
            token = request_context.set(
                {
                    "id": f"req_{thread_id}",
                    "actor": thread_id,
                }
            )

            bind_context_dict(task=thread_id * 10)
            time.sleep(0.1)  # Simulate different timings / race conditions
            logger.info(f"{thread_id}")
            request_context.reset(token)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            executor.map(worker, range(num_threads))

        assert len(caplog_loguru.records) == num_threads

        for record in caplog_loguru.records:
            thread_id_from_msg = int(record["message"])

            extra = record["extra"]

            assert extra["id"] == f"req_{thread_id_from_msg}"
            assert extra["actor"] == thread_id_from_msg
            assert extra["task"] == thread_id_from_msg * 10

            assert len(extra) == 3

    def test_context_cleanup_isolation(self, caplog_loguru):
        token = request_context.set({"id": "first-request", "actor": 1})
        logger.info("Inside request.")
        request_context.reset(token)

        logger.info("Outside request.")

        assert len(caplog_loguru.records) == 2
        assert caplog_loguru.records[0]["extra"]["id"] == "first-request"
        assert "id" not in caplog_loguru.records[1]["extra"]

    def test_multiple_token_context_isolation(self, caplog_loguru):
        first_token = request_context.set({"id": "first-request", "actor": 1})

        logger.info("First token message.")
        second_token = request_context.set({"id": "second-request", "actor": 2})

        logger.info("Second token message.")
        request_context.reset(second_token)

        logger.info("First token message 2.")
        request_context.reset(first_token)

        assert len(caplog_loguru.records) == 3

        assert caplog_loguru.records[0]["extra"]["id"] == "first-request"
        assert caplog_loguru.records[0]["extra"]["actor"] == 1

        assert caplog_loguru.records[1]["extra"]["id"] == "second-request"
        assert caplog_loguru.records[1]["extra"]["actor"] == 2

        assert caplog_loguru.records[2]["extra"]["id"] == "first-request"
        assert caplog_loguru.records[2]["extra"]["actor"] == 1
