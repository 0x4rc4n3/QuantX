"""
Layer: 0
Depends on: quantx_core.impls.system_clock.SystemClock
Implements: pytest test functions for SystemClock
Outside: Testing anything other than SystemClock.
Inside: Verifies SystemClock returns timezone-aware UTC datetime and non-decreasing timestamps.
Security notes: See test_sr_14_clock_never_defaults.py for injection discipline.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from quantx_core.impls.system_clock import SystemClock


def test_system_clock_returns_timezone_aware_utc() -> None:
    clock = SystemClock()
    t = clock.now()
    assert isinstance(t, datetime)
    assert t.tzinfo is not None
    assert t.tzinfo == timezone.utc


def test_system_clock_monotonic_progression() -> None:
    clock = SystemClock()
    t1 = clock.now()
    time.sleep(0.001)
    t2 = clock.now()
    assert t2 >= t1
