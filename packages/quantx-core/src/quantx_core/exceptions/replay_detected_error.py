"""
Layer: 0
Depends on: None
Implements: ReplayDetectedError
Outside: Deciding when to raise it is each caller's concern when ReplayStore.consume_once() returns False.
Inside: Typed exception carrying message and replayed token context.
Security notes: SR-11 / FR-4.2. Signals replay of challenge nonces, session tokens, backup codes, or push approvals.
"""

from __future__ import annotations

from typing import Any


class ReplayDetectedError(Exception):
    """
    Raised when a replay attempt is detected on a single-use token or credential.
    """

    def __init__(
        self,
        message: str,
        token: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.token = token
        self.context = context or {}
