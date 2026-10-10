"""Threshold policy definition with duplicate key rejection at creation time.

Layer: 8
Depends on: quantx_core.types.algorithm_id.AlgorithmId
Implements: ThresholdPolicy immutable definition and validation
Outside: Runtime approval tracking and quorum finalization
Inside: Policy construction, quorum bounds checking, and duplicate-key detection
Security notes: SR-12 in full: duplicate keys rejected at policy creation, never deferred to use time.
"""

from __future__ import annotations

from typing import Sequence

from quantx_core.types.algorithm_id import AlgorithmId

GATE_REVIEW_REQUIRED: bool = True


class ThresholdPolicy:
    """Immutable m-of-n threshold policy rejecting duplicate keys at creation time (SR-12)."""

    def __init__(
        self,
        policy_id: str,
        keys: Sequence[tuple[AlgorithmId, bytes] | bytes],
        m: int,
    ) -> None:
        if not policy_id:
            raise ValueError("policy_id cannot be empty")
        if not keys:
            raise ValueError("keys cannot be empty")

        n = len(keys)
        if m < 1 or m > n:
            raise ValueError(f"Quorum threshold m={m} out of bounds: must satisfy 1 <= m <= n={n}")

        # Detect duplicate public keys (SR-12, FR-8.1)
        seen_keys: set[bytes] = set()
        normalized_keys: list[tuple[AlgorithmId | None, bytes]] = []

        for item in keys:
            if isinstance(item, tuple):
                alg, key_bytes = item
            else:
                alg, key_bytes = None, item

            if key_bytes in seen_keys:
                raise ValueError(
                    f"Duplicate key detected in threshold policy '{policy_id}' (SR-12)"
                )
            seen_keys.add(key_bytes)
            normalized_keys.append((alg, key_bytes))

        self._policy_id = policy_id
        self._keys = tuple(normalized_keys)
        self._m = m
        self._n = n

    @property
    def policy_id(self) -> str:
        return self._policy_id

    @property
    def m(self) -> int:
        return self._m

    @property
    def n(self) -> int:
        return self._n

    @property
    def keys(self) -> tuple[tuple[AlgorithmId | None, bytes], ...]:
        return self._keys

    def is_member_key(self, key_bytes: bytes) -> bool:
        """Check if public key bytes belong to this threshold policy."""
        return any(k[1] == key_bytes for k in self._keys)
