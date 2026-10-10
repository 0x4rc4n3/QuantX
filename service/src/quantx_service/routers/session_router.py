"""Session token validation router for QuantX REST sidecar.

Layer: sidecar
Depends on: quantx_service.wiring.get_orchestrator, quantx_service.wiring.get_dependencies, quantx_service.errors.not_found_error.NotFoundError
Implements: HTTP endpoints GET /v1/session/{token_id} and GET /v1/sessions/{token_id} per 08-api-specification.md
Outside: Business logic and token validation mechanics (handled by SessionOrchestrator)
Inside: Request routing, validating token existence and expiration, shaping session status response
Security notes: Returns 404 not_found for expired or non-existent tokens without leaking internal store structures.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from quantx_service.errors.not_found_error import NotFoundError
from quantx_service.wiring import (
    AppDependencies,
    SessionOrchestrator,
    SessionToken,
    get_dependencies,
    get_orchestrator,
)

router = APIRouter(prefix="/v1", tags=["session"])


class SessionResponse(BaseModel):
    valid: bool
    subject_id: str
    factors_completed: list[str]


@router.get("/session/{token_id}", response_model=SessionResponse)
@router.get("/sessions/{token_id}", response_model=SessionResponse)
async def get_session(
    token_id: str,
    deps: AppDependencies = Depends(get_dependencies),
    orchestrator: SessionOrchestrator = Depends(get_orchestrator),
) -> dict[str, Any]:
    """Retrieve and validate an active session token."""
    if not token_id or not token_id.strip():
        raise NotFoundError("Token ID must be non-empty")

    cleaned_id = token_id.strip()
    is_valid = orchestrator.validate(cleaned_id)
    if not is_valid:
        raise NotFoundError(f"Session token '{cleaned_id}' not found or expired")

    token_key = f"session:{cleaned_id}"
    raw_token = deps.kv_store.get(token_key)
    if raw_token is None:
        raise NotFoundError(f"Session token '{cleaned_id}' not found or expired")

    try:
        token = SessionToken.from_json(raw_token.decode("utf-8"))
    except Exception as exc:
        raise NotFoundError(f"Session token could not be parsed: {exc}") from exc

    return {
        "valid": True,
        "subject_id": token.subject_id,
        "factors_completed": list(token.factors_completed),
    }
