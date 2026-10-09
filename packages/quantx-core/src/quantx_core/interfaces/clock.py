"""
Layer: 0
Depends on: None
Implements: Clock
Outside: TTL and expiry calculations; performed by callers using returned datetime.
Inside: The now() -> datetime method signature returning timezone-aware UTC datetime.
Security notes: SR-14 / FR-0.3. Clock is always injected; direct wall-clock reads or or-defaulted fallbacks are forbidden.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """
    Foundational interface for time measurement and timestamp generation.
    """

    def now(self) -> datetime:
        """
        Returns the current time as a timezone-aware UTC datetime.
        """
        ...
