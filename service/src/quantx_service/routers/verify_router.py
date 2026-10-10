"""Verification router for QuantX REST sidecar.

Layer: sidecar
Depends on: quantx_service.wiring.get_orchestrator, quantx_service.wiring.get_dependencies, quantx_service.errors.verification_failed_error.VerificationFailedError, quantx_service.errors.not_found_error.NotFoundError, quantx_service.errors.malformed_request_error.MalformedRequestError
Implements: HTTP endpoint POST /v1/verify per 08-api-specification.md
Outside: Cryptographic verification algorithms and combiner logic (handled by Layer 2 and Layer 4)
Inside: Request decoding, server-side mode enforcement, invoking SessionOrchestrator, and shaping session token response
Security notes: SR-1 (sidecar boundary): Never trusts client-declared mode from the wire; required_mode is determined exclusively from server state.
"""

from __future__ import annotations

import base64
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.exceptions.rate_limited_error import RateLimitedError
from quantx_core.exceptions.replay_detected_error import ReplayDetectedError

from quantx_service.errors.already_consumed_error import AlreadyConsumedError
from quantx_service.errors.malformed_request_error import MalformedRequestError
from quantx_service.errors.not_found_error import NotFoundError
from quantx_service.errors.rate_limited_error import RateLimitedHTTPError
from quantx_service.errors.verification_failed_error import VerificationFailedError
from quantx_service.wiring import (
    AppDependencies,
    ChallengeRecord,
    SessionOrchestrator,
    get_dependencies,
    get_orchestrator,
)

router = APIRouter(prefix="/v1", tags=["verify"])


class VerifyRequest(BaseModel):
    challenge_id: str = Field(..., description="Challenge ID to verify against")
    signature: str = Field(..., description="Base64-encoded combined signature wire bytes")
    declared_mode: str | None = Field(
        default=None, description="Client-declared mode for wire formatting"
    )


class VerifyResponse(BaseModel):
    session_token: str
    expires_at: str


@router.post("/verify", response_model=VerifyResponse)
async def verify_challenge(
    request: VerifyRequest,
    deps: AppDependencies = Depends(get_dependencies),
    orchestrator: SessionOrchestrator = Depends(get_orchestrator),
) -> dict[str, Any]:
    """Verify signed challenge response and issue authenticated session token."""
    if not request.challenge_id or not request.challenge_id.strip():
        raise MalformedRequestError("Field 'challenge_id' must be non-empty")

    if not request.signature:
        raise MalformedRequestError("Field 'signature' must be non-empty")

    try:
        sig_bytes = base64.b64decode(request.signature)
    except Exception as exc:
        raise MalformedRequestError("Field 'signature' must be valid base64-encoded bytes") from exc

    # Fetch challenge record to check existence and server required mode
    chal_key = f"challenge:{request.challenge_id}"
    raw_chal = deps.kv_store.get(chal_key)
    if raw_chal is None:
        chal_consumed_key = f"replay:chal_consumed:{request.challenge_id}"
        if deps.kv_store.get(chal_consumed_key) is not None:
            raise AlreadyConsumedError(
                f"Challenge '{request.challenge_id}' has already been consumed"
            )
        raise NotFoundError(f"Challenge '{request.challenge_id}' not found or expired")

    try:
        record = ChallengeRecord.from_json(raw_chal.decode("utf-8"))
    except Exception as exc:
        raise MalformedRequestError(f"Invalid challenge record in store: {exc}") from exc

    # SR-1 sidecar-boundary enforcement:
    # If client attempts to declare a mode that does not match server required mode, reject immediately
    if request.declared_mode is not None:
        req_mode_str = (
            record.required_mode.value
            if hasattr(record.required_mode, "value")
            else str(record.required_mode)
        )
        if request.declared_mode != req_mode_str:
            raise VerificationFailedError(
                f"Mode mismatch: declared mode '{request.declared_mode}' does not match server required mode '{req_mode_str}'"
            )

    try:
        token = orchestrator.finish(
            challenge_id=request.challenge_id,
            signed_response=sig_bytes,
        )
    except ReplayDetectedError as exc:
        raise AlreadyConsumedError(str(exc)) from exc
    except RateLimitedError as exc:
        raise RateLimitedHTTPError(str(exc)) from exc
    except MalformedInputError as exc:
        err_msg = str(exc)
        if "not found or expired" in err_msg or "expired" in err_msg:
            raise NotFoundError(err_msg) from exc
        raise VerificationFailedError(err_msg) from exc
    except Exception as exc:
        raise VerificationFailedError(f"Verification failed: {exc}") from exc

    return {
        "session_token": token.token_id,
        "expires_at": token.expires_at.isoformat(),
    }
