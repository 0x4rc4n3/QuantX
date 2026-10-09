"""
Layer: 0
Depends on: None
Implements: MalformedInputError
Outside: Deciding when to raise it is each parser's concern; Verifier.verify() catches this and returns False (FR-0.1).
Inside: Typed exception carrying message and structured context for unparseable or invalid binary/wire input.
Security notes: FR-0.1 / Mandatory fuzzing test 5. Raised on invalid length prefixes or corrupt wire formats; prevents out-of-bounds reads.
"""

from __future__ import annotations

from typing import Any


class MalformedInputError(Exception):
    """
    Raised when binary wire format or cryptographic input cannot be parsed or violates size bounds.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}
