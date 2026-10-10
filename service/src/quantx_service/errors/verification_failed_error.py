"""Verification failed error mapping and handler.

Layer: sidecar
Depends on: error_envelope.py
Implements: FastAPI exception handler mapping verification failures to 401 verification_failed
Outside: Any other error kind — one file per error kind, per 14-directory-structure.md
Inside: The 401/verification_failed mapping and error_envelope.py shaping
Security notes: Ensures verification failures and mode mismatches surface as 401 without handing distinguishing oracles to callers.
"""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from quantx_service.errors.error_envelope import ServiceError, create_error_response


class VerificationFailedError(ServiceError):
    """Exception raised when signature verification fails or mode mismatch is detected."""

    def __init__(self, message: str = "Verification failed", details: Any = None) -> None:
        super().__init__(
            code="verification_failed",
            message=message,
            status_code=401,
            details=details,
        )


async def verification_failed_handler(request: Request, exc: Exception) -> JSONResponse:
    """Exception handler mapping verification failure exceptions to 401 verification_failed."""
    details = getattr(exc, "details", None)
    message = str(getattr(exc, "message", "Verification failed"))
    return create_error_response(
        status_code=401,
        code="verification_failed",
        message=message,
        details=details,
    )
