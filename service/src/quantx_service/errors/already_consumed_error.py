"""Already consumed error mapping and handler.

Layer: sidecar
Depends on: error_envelope.py, quantx_core.exceptions.replay_detected_error.ReplayDetectedError
Implements: FastAPI exception handler mapping replay errors to 409 already_consumed
Outside: Any other error kind — one file per error kind, per 14-directory-structure.md
Inside: The 409/already_consumed mapping and error_envelope.py shaping
Security notes: Ensures replay attempts surface as 409 already_consumed per 08-api-specification.md.
"""

from __future__ import annotations

from typing import Any

from quantx_core.exceptions.replay_detected_error import ReplayDetectedError
from starlette.requests import Request
from starlette.responses import JSONResponse

from quantx_service.errors.error_envelope import ServiceError, create_error_response


class AlreadyConsumedError(ServiceError):
    """Exception raised when a challenge or token has already been consumed."""

    def __init__(
        self, message: str = "Challenge or token has already been consumed", details: Any = None
    ) -> None:
        super().__init__(
            code="already_consumed",
            message=message,
            status_code=409,
            details=details,
        )


async def already_consumed_handler(request: Request, exc: Exception) -> JSONResponse:
    """Exception handler mapping replay and already consumed exceptions to 409 already_consumed."""
    details = getattr(exc, "details", None)
    message = str(getattr(exc, "message", "Challenge or token has already been consumed"))
    if isinstance(exc, ReplayDetectedError):
        message = "Challenge or token has already been consumed"
    return create_error_response(
        status_code=409,
        code="already_consumed",
        message=message,
        details=details,
    )
