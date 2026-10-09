"""
Layer: 0
Depends on: quantx_core.interfaces.clock.Clock
Implements: SystemClock
Outside: Anything not directly part of the Clock contract.
Inside: Concrete Clock implementation reading system time in UTC.
Security notes: SR-14. The only file permitted to read wall-clock time; clock is always injected.
"""

from __future__ import annotations

from datetime import datetime, timezone

from quantx_core.interfaces.clock import Clock


class SystemClock(Clock):
    """
    Production Clock implementation reading the host system time in UTC.
    """

    def now(self) -> datetime:
        """
        Returns the current time as a timezone-aware UTC datetime.
        """
        return datetime.now(timezone.utc)
