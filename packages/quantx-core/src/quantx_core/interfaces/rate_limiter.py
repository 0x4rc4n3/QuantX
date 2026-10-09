"""
Layer: 0
Depends on: None
Implements: RateLimiter
Outside: Selecting which identity keys to gate on and wiring independent limiter instances.
Inside: The allow(identity_key: str) -> bool check-and-count method signature.
Security notes: FR-4.4 / FR-5.2 / SR-5. Independent limiter instances protect challenges, TOTP, and push issuance.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class RateLimiter(Protocol):
    """
    Foundational interface for rate limiting.
    """

    def allow(self, identity_key: str) -> bool:
        """
        Checks whether an attempt for identity_key is within allowed limits, counting the attempt.

        Returns True if allowed, False if the limit has been reached or exceeded.
        """
        ...
