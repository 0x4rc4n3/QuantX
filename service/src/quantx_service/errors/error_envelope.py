"""Error envelope module for QuantX REST sidecar.

Layer: sidecar
Depends on: none
Implements: Single consistent JSON error envelope per 08-api-specification.md
Outside: Business logic and router execution
Inside: Error payload shaping and JSONResponse generation
Security notes: Ensures uniform error responses across endpoints without leaking internal stack traces or implementation details.
"""

from __future__ import annotations

from typing import Any

from starlette.responses import JSONResponse


class ServiceError(Exception):
    """Base class for sidecar HTTP-mapped errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        details: Any = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        self.headers = headers or {}


def make_error_payload(code: str, message: str, details: Any = None) -> dict[str, Any]:
    """Build the canonical error envelope dictionary.

    Shapes response as:
    {"error": {"code": code, "error_code": code, "message": message, "details": ...}}
    """
    payload: dict[str, Any] = {
        "code": code,
        "error_code": code,
        "message": message,
    }
    if details is not None:
        payload["details"] = details
    return {"error": payload}


def create_error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Create a Starlette/FastAPI JSONResponse containing the standardized error envelope."""
    payload = make_error_payload(code=code, message=message, details=details)
    return JSONResponse(status_code=status_code, content=payload, headers=headers)
