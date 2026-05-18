from typing import Any, Callable
from uuid import uuid4

from django.http import HttpRequest, HttpResponse

from .utils import request_context


class RequestContextLogMiddleware:
    def __init__(self, get_response: Callable[[Any], Any]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        token = request_context.set(
            {
                "id": str(uuid4()),
                "actor": getattr(request.user, "id", None),
                "path": request.path,
                "method": request.method,
            }
        )

        try:
            return self.get_response(request)
        finally:
            request_context.reset(token)
