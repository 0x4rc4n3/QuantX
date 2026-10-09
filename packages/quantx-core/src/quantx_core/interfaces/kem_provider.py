"""
Layer: 0
Depends on: None
Implements: KEMProvider
Outside: HKDF binding of ciphertext and public key into info parameter (Layer 2 KEMCombiner, SR-7).
Inside: The encapsulate and decapsulate method signatures for KEM adapters.
Security notes: Ciphertext and public-key binding is enforced by KEMCombiner, not by this Protocol.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class KEMProvider(Protocol):
    """
    Foundational interface for Key Encapsulation Mechanism (KEM) operations.
    """

    def encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]:
        """
        Encapsulates a shared secret against the target public key.

        Returns tuple of (ciphertext, shared_secret).
        Raises typed error on malformed public key or internal failure.
        """
        ...

    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> bytes:
        """
        Decapsulates a shared secret from the ciphertext using the private key.

        Returns the shared secret bytes.
        Raises typed error on malformed ciphertext/key or decapsulation failure.
        """
        ...
