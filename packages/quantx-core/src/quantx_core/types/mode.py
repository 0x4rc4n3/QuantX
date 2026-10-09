"""
Layer: 0
Depends on: None
Implements: Mode
Outside: Two verifiers in the same deployment configured with different required_mode values for the same role is a config error caught at registry-load time, not a runtime ambiguity this type resolves at the value level.
Inside: String-backed Enum with HYBRID, PQC_ONLY, and CLASSICAL_ONLY.
Security notes: Mode is a server-side construction fact, never trusted from wire data (P4, SR-1).
"""

from __future__ import annotations

from enum import Enum


class Mode(str, Enum):
    """
    Formally types the three modes QuantX runs in: HYBRID, PQC_ONLY, CLASSICAL_ONLY.
    """

    HYBRID = "HYBRID"
    PQC_ONLY = "PQC_ONLY"
    CLASSICAL_ONLY = "CLASSICAL_ONLY"

    def __str__(self) -> str:
        return self.value
