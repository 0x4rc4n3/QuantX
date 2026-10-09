"""
Layer: 0
Depends on: None
Implements: Canonicalizer
Outside: Deciding what structured data gets canonicalized and signed is each caller's responsibility.
Inside: The canonicalize(data: Mapping[str, object]) -> bytes method signature.
Security notes: SR-8 / FR-0.4. Exactly one canonicalization path is permitted system-wide (JCSCanonicalizer).
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable


@runtime_checkable
class Canonicalizer(Protocol):
    """
    Foundational interface for deterministic serialization of structured data for signing.
    """

    def canonicalize(self, data: Mapping[str, Any]) -> bytes:
        """
        Deterministically converts structured mapping data into canonical bytes.

        Raises MalformedInputError or TypeError if data is not canonicalizable.
        """
        ...
