import inspect
import logging
import sys
from typing import Any

from loguru import logger

from .utils import request_context


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class TmsLogger:
    format: str = (
        "<green>{time:YYYY-MM-DD--HH:mm:ss}</green> | <level>{level: <9}</level> | {extra} |"
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    def __init__(self, level: int | str) -> None:
        def patch_with_context(record: dict[str, Any]) -> None:
            context_data = request_context.get()
            if context_data:
                record["extra"].update(context_data)

        logger.configure(patcher=patch_with_context)

        try:
            logger.remove(0)
        except ValueError:
            pass

        logger.add(
            sink="logs/tms.logs",
            colorize=False,
            enqueue=True,
            format=self.format,
            rotation="500 MB",
            retention=5,
        )
        logger.add(
            sink=sys.stderr,
            colorize=True,
            enqueue=True,
            format=self.format,
        )
        logging.basicConfig(handlers=[InterceptHandler()], level=level, force=True)
