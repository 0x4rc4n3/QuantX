"""Rate limited error mapping and handler.

Layer: sidecar
Depends on: error_envelope.py, quantx_core.exceptions.rate_limited_error.RateLimitedError
Implements: FastAPI exception handler mapping rate limiting errors to 429 rate_limited
Outside: Any other error kind — one file per error kind, per 14-directory-structure.md
Inside: The 429/rate_limited mapping, Retry-After header setting, and error_envelope.py shaping
Security notes: Ensures rate-limit trips surface as 429 rate_limited with standard Retry-After guidance.
"""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from quantx_service.errors.error_envelope import ServiceError, create_error_response


class RateLimitedHTTPError(ServiceError):
    """Exception raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = 60,
        details: Any = None,
    ) -> None:
        super().__init__(
            code="rate_limited",
            message=message,
            status_code=429,
            details=details,
            headers={"Retry-After": str(retry_after)},
        )
        self.retry_after = retry_after


async def rate_limited_handler(request: Request, exc: Exception) -> JSONResponse:
    """Exception handler mapping rate limited exceptions to 429 rate_limited."""
    details = getattr(exc, "details", None)
    message = str(getattr(exc, "message", "Rate limit exceeded"))
    retry_after = getattr(exc, "retry_after", 60)
    headers = {"Retry-After": str(retry_after)}
    return create_error_response(
        status_code=429,
        code="rate_limited",
        message=message,
        details=details,
        headers=headers,
    )
