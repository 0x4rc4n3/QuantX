"""
Layer: 0
Depends on: None
Implements: Verifier
Outside: Deciding which algorithm verifier is in play is the concern of the registry and combiner.
Inside: The verify(message: bytes, signature: bytes) -> bool method signature.
Security notes: FR-0.1. Verifier.verify() never raises; internal errors (malformed bytes, wrong key length) are caught and converted to False.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Verifier(Protocol):
    """
    Foundational interface for classical and post-quantum verification operations.
    """

    def verify(self, message: bytes, signature: bytes) -> bool:
        """
        Verifies the signature against the message.

        Must never raise on invalid or malformed signature/key data; returns False instead (FR-0.1).
        """
        ...
