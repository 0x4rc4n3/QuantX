"""Backend unavailable error mapping and handler.

Layer: sidecar
Depends on: error_envelope.py, quantx_core.exceptions.backend_unavailable_error.BackendUnavailableError
Implements: FastAPI exception handler mapping backend outages to 503 backend_unavailable
Outside: Any other error kind — one file per error kind, per 14-directory-structure.md
Inside: The 503/backend_unavailable mapping and error_envelope.py shaping
Security notes: Ensures backend outages surface as 503 backend_unavailable rather than generic 500s.
"""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from quantx_service.errors.error_envelope import ServiceError, create_error_response


class BackendUnavailableHTTPError(ServiceError):
    """Exception raised when an underlying storage or custody backend is unreachable."""

    def __init__(
        self, message: str = "Underlying backend unavailable", details: Any = None
    ) -> None:
        super().__init__(
            code="backend_unavailable",
            message=message,
            status_code=503,
            details=details,
        )


async def backend_unavailable_handler(request: Request, exc: Exception) -> JSONResponse:
    """Exception handler mapping backend unavailable exceptions to 503 backend_unavailable."""
    details = getattr(exc, "details", None)
    message = str(getattr(exc, "message", "Underlying backend unavailable"))
    return create_error_response(
        status_code=503,
        code="backend_unavailable",
        message=message,
        details=details,
    )
