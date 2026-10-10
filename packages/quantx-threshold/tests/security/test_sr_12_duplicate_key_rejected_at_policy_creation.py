"""Mandatory security test SR-12: Duplicate key rejected at policy creation time.

Layer: 8
Depends on: quantx_core.types.algorithm_id.AlgorithmId, quantx_threshold.threshold_policy.ThresholdPolicy
Implements: SR-12 mandatory test verifying duplicate key rejection at construction time
Outside: Runtime approval tracking and finalization
Inside: Detection and rejection of identical public keys in candidate policy key set
Security notes: SR-12: Duplicate keys rejected at policy creation time, never deferred to use time.
"""

from __future__ import annotations

import pytest
from quantx_core.types.algorithm_id import AlgorithmId
from quantx_threshold.threshold_policy import ThresholdPolicy


def test_sr_12_duplicate_key_rejected_at_policy_creation() -> None:
    identical_key = b"\xaa" * 32
    distinct_key = b"\xbb" * 32

    # Attempt to construct policy with identical key supplied twice
    keys = [
        (AlgorithmId.ED25519, identical_key),
        (AlgorithmId.ED25519, distinct_key),
        (AlgorithmId.ED25519, identical_key),  # DUPLICATE
    ]

    with pytest.raises(ValueError, match="Duplicate key detected"):
        ThresholdPolicy(policy_id="vulnerable-board-policy", keys=keys, m=2)


def test_sr_12_duplicate_raw_key_bytes_rejected() -> None:
    duplicate_raw_key = b"\xcc" * 32
    keys = [
        duplicate_raw_key,
        b"\xdd" * 32,
        duplicate_raw_key,  # DUPLICATE
    ]

    with pytest.raises(ValueError, match="Duplicate key detected"):
        ThresholdPolicy(policy_id="raw-keys-policy", keys=keys, m=2)
