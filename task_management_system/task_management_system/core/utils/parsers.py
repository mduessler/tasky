from loguru import logger
from rest_framework.exceptions import ParseError
from rest_framework.views import Request


def get_int_query_param(request: Request, name: str) -> int | None:
    if (value := request.query_params.get(name)) is None:
        logger.warning(f"Invalid query parameter: {name}.")
        return None
    try:
        result = int(value)
        logger.debug(f"Converted {value} to integer.")
        return result
    except ValueError as exc:
        logger.warning(f"Invalid value: {value}.")
        raise ParseError(exc)
