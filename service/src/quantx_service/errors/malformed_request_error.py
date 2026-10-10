"""Malformed request error mapping and handler.

Layer: sidecar
Depends on: error_envelope.py
Implements: FastAPI exception handler mapping malformed request errors to 400 malformed_request
Outside: Any other error kind — one file per error kind, per 14-directory-structure.md
Inside: The 400/malformed_request mapping and error_envelope.py shaping
Security notes: Ensures malformed request failures are surfaced accurately rather than collapsed into generic 500s.
"""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from quantx_service.errors.error_envelope import ServiceError, create_error_response


class MalformedRequestError(ServiceError):
    """Exception raised when a request body fails validation or contains unparseable data."""

    def __init__(
        self, message: str = "Request body is malformed or invalid", details: Any = None
    ) -> None:
        super().__init__(
            code="malformed_request",
            message=message,
            status_code=400,
            details=details,
        )


async def malformed_request_handler(request: Request, exc: Exception) -> JSONResponse:
    """Exception handler mapping malformed request exceptions to 400 malformed_request."""
    details = getattr(exc, "details", None)
    message = str(getattr(exc, "message", "Request body is malformed or invalid"))
    return create_error_response(
        status_code=400,
        code="malformed_request",
        message=message,
        details=details,
    )
