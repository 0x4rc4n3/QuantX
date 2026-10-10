"""Not found error mapping and handler.

Layer: sidecar
Depends on: error_envelope.py
Implements: FastAPI exception handler mapping not found exceptions to 404 not_found
Outside: Any other error kind — one file per error kind, per 14-directory-structure.md
Inside: The 404/not_found mapping and error_envelope.py shaping
Security notes: Ensures unknown or expired resource references surface as 404 rather than generic 500s.
"""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from quantx_service.errors.error_envelope import ServiceError, create_error_response


class NotFoundError(ServiceError):
    """Exception raised when a challenge or session is unknown or has expired."""

    def __init__(self, message: str = "Resource not found or expired", details: Any = None) -> None:
        super().__init__(
            code="not_found",
            message=message,
            status_code=404,
            details=details,
        )


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Exception handler mapping not found exceptions to 404 not_found."""
    details = getattr(exc, "details", None)
    message = str(getattr(exc, "message", "Resource not found or expired"))
    return create_error_response(
        status_code=404,
        code="not_found",
        message=message,
        details=details,
    )
