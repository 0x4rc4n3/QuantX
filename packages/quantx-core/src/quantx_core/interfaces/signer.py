"""
Layer: 0
Depends on: None
Implements: Signer
Outside: Choice of concrete algorithm adapter; managed via AlgorithmRegistry and constructor wiring.
Inside: The sign(message: bytes) -> bytes method signature for signature adapters.
Security notes: Protocol carries no security guarantee itself; guarantee depends on the wired adapter.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Signer(Protocol):
    """
    Foundational interface for classical and post-quantum signing operations.
    """

    def sign(self, message: bytes) -> bytes:
        """
        Signs the given message and returns signature bytes.

        Raises an explicit exception on backend or cryptographic failure.
        """
        ...
