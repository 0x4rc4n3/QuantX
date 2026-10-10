"""Hybrid TLS 1.3 group enforcement ASGI middleware.

Layer: sidecar
Depends on: quantx_service.config.ServiceConfig, quantx_service.errors.error_envelope.create_error_response
Implements: ASGI middleware inspecting and enforcing required hybrid TLS key exchange groups
Outside: Application-layer signature mode enforcement (handled by SignatureCombiner / SR-1)
Inside: Inspecting ASGI connection TLS parameters and rejecting non-hybrid or missing TLS groups when enforcement is required
Security notes: Transport-layer analogue of SR-1 preventing silent downgrade attacks at the network boundary per D-016.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, MutableMapping

from quantx_service.errors.error_envelope import create_error_response

REQUIRED_HYBRID_GROUPS = {"x25519mlkem768", "x25519_mlkem768", "x25519-mlkem768"}


class HybridTLSEnforcementMiddleware:
    """Middleware enforcing hybrid TLS 1.3 key-exchange groups."""

    def __init__(
        self,
        app: Any,
        tls_enforcement: str = "off",
    ) -> None:
        self.app = app
        self.enforcement = tls_enforcement.lower()

    async def __call__(
        self,
        scope: MutableMapping[str, Any],
        receive: Callable[..., Awaitable[Any]],
        send: Callable[[MutableMapping[str, Any]], Awaitable[None]],
    ) -> None:
        if scope["type"] != "http" or self.enforcement != "required":
            await self.app(scope, receive, send)
            return

        # Fail-closed check: inspect connection TLS group
        tls_info = scope.get("tls", {})
        tls_group = scope.get("tls_group") or (
            tls_info.get("group") if isinstance(tls_info, dict) else None
        )

        if not tls_group or str(tls_group).lower() not in REQUIRED_HYBRID_GROUPS:
            response = create_error_response(
                status_code=400,
                code="malformed_request",
                message="Transport connection does not satisfy required hybrid TLS 1.3 group (X25519MLKEM768)",
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
