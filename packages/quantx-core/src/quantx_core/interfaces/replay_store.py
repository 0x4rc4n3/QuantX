"""
Layer: 0
Depends on: quantx_core.types.ttl.TTL
Implements: ReplayStore
Outside: Semantic classification of tokens (challenge IDs, session tokens, backup codes, push approvals).
Inside: The consume_once method signature providing atomic single-use semantics.
Security notes: SR-11 / FR-4.2. Every replay-sensitive credential must be consumed via this interface.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from quantx_core.types.ttl import TTL


@runtime_checkable
class ReplayStore(Protocol):
    """
    Foundational interface for single-use replay protection.
    """

    def consume_once(self, token: str, ttl: TTL | None = None) -> bool:
        """
        Attempts to consume a token.

        Returns True on the first successful consumption, and False on any subsequent attempt.
        """
        ...
