"""Shared utilities for API routers."""

from fastapi.responses import JSONResponse


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """Build a unified error response.

    Args:
        status_code: HTTP status code.
        code: Machine-readable error code.
        message: Human-readable error description.

    Returns:
        JSONResponse with the standard error envelope.
    """
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )
