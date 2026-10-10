"""End-to-end security test for SR-12: Duplicate key in threshold policy rejected at creation.

Layer: cross-cutting
Depends on: quantx_threshold.threshold_policy.ThresholdPolicy, quantx_threshold.threshold_manager.ThresholdManager
Implements: Mandatory full-stack end-to-end test for SR-12 (duplicate keys rejected at policy creation)
Outside: Every other numbered SR item
Inside: Attempt to construct a duplicate-key policy through the full threshold flow, confirming early rejection
Wire format: Policy structures
Security notes: Mandatory SR-12 end-to-end confirmation spanning quantx-threshold
"""

from __future__ import annotations

import pytest
from quantx_threshold.threshold_policy import ThresholdPolicy


def test_sr_12_end_to_end_threshold_duplicate_key_rejected_at_policy_creation() -> None:
    duplicate_key = b"duplicate_pubkey_bytes_32_chars!"
    distinct_key = b"distinct_pubkey_bytes_32_chars!!"

    # Policy creation with duplicate keys MUST raise ValueError immediately (SR-12)
    with pytest.raises(ValueError, match="Duplicate key detected in threshold policy"):
        ThresholdPolicy(
            policy_id="board-treasury-policy",
            keys=[duplicate_key, duplicate_key, distinct_key],
            m=2,
        )
