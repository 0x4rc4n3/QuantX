"""Bearer token authentication dependency for QuantX REST sidecar clients.

Layer: sidecar
Depends on: quantx_service.config.ServiceConfig, quantx_service.errors.verification_failed_error.VerificationFailedError
Implements: FastAPI dependency validating client Authorization: Bearer <token> header
Outside: End-user subject authentication (handled via challenge-response)
Inside: Bearer token extraction and constant-time validation against configured tokens
Security notes: Constant-time comparison prevents timing side-channels during client authentication per 09-auth-and-authorization.md.
"""

from __future__ import annotations

import hmac

from starlette.requests import Request

from quantx_service.config import ServiceConfig
from quantx_service.errors.verification_failed_error import VerificationFailedError


class BearerTokenAuth:
    """Dependency verifying sidecar client bearer tokens."""

    def __init__(self, allowed_tokens: list[str] | set[str] | None = None) -> None:
        self._allowed_tokens = set(allowed_tokens or [])

    @classmethod
    def from_config(cls, config: ServiceConfig) -> BearerTokenAuth:
        tokens: list[str] = []
        token_val = config.service.get("bearer_token")
        if token_val and isinstance(token_val, str):
            tokens.append(token_val)
        return cls(tokens)

    def __call__(self, request: Request) -> bool:
        if not self._allowed_tokens:
            # If no bearer tokens are configured, allow requests in dev/test
            return True

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise VerificationFailedError("Missing or invalid Authorization header")

        token = auth_header[7:].strip()
        for allowed in self._allowed_tokens:
            if hmac.compare_digest(token, allowed):
                return True

        raise VerificationFailedError("Invalid client bearer token")
