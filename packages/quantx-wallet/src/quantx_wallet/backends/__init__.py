"""Custody backends for QuantX key wallet.

Layer: 6
Depends on: Nothing
Implements: Package exports for custody backends
Outside: Wallet orchestration and session management
Inside: Exposes custody backend implementations and interfaces
Security notes: Real integrations or explicit typed errors; resident keys never exported.
"""

from __future__ import annotations

__all__: list[str] = []
