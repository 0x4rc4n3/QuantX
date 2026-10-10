"""Unit tests for ThresholdPolicy structural validation.

Layer: 8
Depends on: quantx_core.types.algorithm_id.AlgorithmId, quantx_threshold.threshold_policy.ThresholdPolicy
Implements: Pytest tests validating policy construction, properties, and m-bound checks
Outside: SR-12 duplicate key rejection (tested in security suite)
Inside: Valid policy creation, member key checks, and out-of-range m validation
Security notes: Validates policy structure and bounds checks.
"""

from __future__ import annotations

import pytest
from quantx_core.types.algorithm_id import AlgorithmId
from quantx_threshold.threshold_policy import ThresholdPolicy


def test_threshold_policy_valid_construction(
    sample_keys: list[tuple[AlgorithmId, bytes]],
) -> None:
    policy = ThresholdPolicy(policy_id="policy-1", keys=sample_keys, m=2)
    assert policy.policy_id == "policy-1"
    assert policy.m == 2
    assert policy.n == 3
    assert policy.is_member_key(sample_keys[0][1]) is True
    assert policy.is_member_key(b"unknown-key-bytes") is False


def test_threshold_policy_invalid_m_rejected(
    sample_keys: list[tuple[AlgorithmId, bytes]],
) -> None:
    # m < 1 rejected
    with pytest.raises(ValueError, match="out of bounds"):
        ThresholdPolicy(policy_id="p1", keys=sample_keys, m=0)

    # m > n rejected
    with pytest.raises(ValueError, match="out of bounds"):
        ThresholdPolicy(policy_id="p2", keys=sample_keys, m=4)


def test_threshold_policy_empty_keys_or_id_rejected() -> None:
    with pytest.raises(ValueError, match="keys cannot be empty"):
        ThresholdPolicy(policy_id="p1", keys=[], m=1)

    with pytest.raises(ValueError, match="policy_id cannot be empty"):
        ThresholdPolicy(policy_id="", keys=[(AlgorithmId.ED25519, b"k1")], m=1)
