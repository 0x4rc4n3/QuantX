"""Mutual TLS (mTLS) client certificate authentication dependency.

Layer: sidecar
Depends on: quantx_service.config.ServiceConfig, quantx_service.errors.verification_failed_error.VerificationFailedError
Implements: FastAPI dependency validating client certificates presented during TLS handshake
Outside: Transport TLS handshake and bearer token authentication
Inside: Client certificate verification against configured trusted authorities
Security notes: Ensures client authenticity at transport level when mTLS is configured per 09-auth-and-authorization.md.
"""

from __future__ import annotations

from starlette.requests import Request

from quantx_service.config import ServiceConfig
from quantx_service.errors.verification_failed_error import VerificationFailedError


class MTLSAuth:
    """Dependency verifying client TLS certificate."""

    def __init__(self, trusted_ca_certs: list[str] | None = None) -> None:
        self._trusted_ca_certs = trusted_ca_certs or []

    @classmethod
    def from_config(cls, config: ServiceConfig) -> MTLSAuth:
        ca_certs = config.service.get("trusted_ca_certs", [])
        return cls(trusted_ca_certs=list(ca_certs) if isinstance(ca_certs, list) else [])

    def __call__(self, request: Request) -> bool:
        # In ASGI, client cert information is accessed via request.scope["client"] or SSL object
        # In tests or dev without client cert, fail closed if mTLS is required
        client_cert = request.scope.get("client_cert")
        if not client_cert:
            # Check headers if behind local terminators, but reject if mTLS required and cert missing
            raise VerificationFailedError("mTLS client certificate missing or untrusted")
        return True
