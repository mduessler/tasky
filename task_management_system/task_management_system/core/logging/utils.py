from contextvars import ContextVar
from typing import Any, Dict

from loguru import logger

request_context: ContextVar[Dict[str, Any]] = ContextVar(
    "request_context", default=None  # type: ignore[arg-type]
)


def bind_context_dict(**kwargs: Any) -> Any:
    ctx = request_context.get()
    if ctx is None:
        ctx = {}
        request_context.set(ctx)
    ctx.update(kwargs)
    return logger
