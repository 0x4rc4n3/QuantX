"""
Layer: 0
Depends on: None
Implements: BackendUnavailableError
Outside: Deciding when to raise it is each storage or custody backend's own concern.
Inside: Typed exception carrying message and optional context for backend failures.
Security notes: SR-4 / SR-6. Storage and custody failures must raise explicitly; silent fallback to weaker storage is prohibited.
"""

from __future__ import annotations

from typing import Any


class BackendUnavailableError(Exception):
    """
    Raised when a storage or key-custody backend is unavailable or encounters a network failure.
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}
