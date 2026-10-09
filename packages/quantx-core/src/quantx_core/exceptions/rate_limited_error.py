"""
Layer: 0
Depends on: None
Implements: RateLimitedError
Outside: Deciding when to raise it is each caller's concern (e.g. SessionOrchestrator, service error handlers).
Inside: Typed exception carrying message, identity key, and retry_after hint.
Security notes: FR-4.4 / FR-5.2 / SR-5. Raised independently when per-identity, global, TOTP, or push-issuance limiters trip.
"""

from __future__ import annotations

from typing import Any


class RateLimitedError(Exception):
    """
    Raised when an operation is rejected because a rate limit threshold has been exceeded.
    """

    def __init__(
        self,
        message: str,
        identity_key: str | None = None,
        retry_after_seconds: int | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.identity_key = identity_key
        self.retry_after_seconds = retry_after_seconds
        self.context = context or {}
