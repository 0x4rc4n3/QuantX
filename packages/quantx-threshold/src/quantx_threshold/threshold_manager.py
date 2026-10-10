"""Threshold manager tracking quorum progress and executing single-shot finalize.

Layer: 8
Depends on: quantx_core.interfaces.replay_store.ReplayStore, quantx_threshold.approval_record.ApprovalRecord, quantx_threshold.threshold_policy.ThresholdPolicy
Implements: ThresholdManager
Outside: Policy construction (ThresholdPolicy) and cryptographic signature primitives
Inside: Approval collection, ReplayStore deduplication, quorum check, and single-shot finalization
Security notes: FR-8.2: finalize() executes only after quorum is reached, and does so exactly once.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol

from quantx_core.interfaces.replay_store import ReplayStore

from quantx_threshold.approval_record import ApprovalRecord
from quantx_threshold.threshold_policy import ThresholdPolicy

GATE_REVIEW_REQUIRED: bool = True


class VerifierInterface(Protocol):
    """Protocol for signature verifier reused by ThresholdManager (P3)."""

    def verify(self, signature: bytes, message: bytes) -> bool: ...


class ThresholdManager:
    """Manages threshold approvals and triggers gated execution once quorum is met."""

    def __init__(
        self,
        policy: ThresholdPolicy,
        verifier: Any,
        replay_store: ReplayStore,
        action: Callable[[], Any] | None = None,
    ) -> None:
        self._policy = policy
        self._verifier = verifier
        self._replay_store = replay_store
        self._action = action
        self._approved_keys: set[str] = set()
        self._finalized: bool = False

    @property
    def policy(self) -> ThresholdPolicy:
        return self._policy

    @property
    def approved_count(self) -> int:
        return len(self._approved_keys)

    @property
    def is_quorum_reached(self) -> bool:
        return len(self._approved_keys) >= self._policy.m

    @property
    def is_finalized(self) -> bool:
        return self._finalized

    def submit_approval(self, approval: ApprovalRecord) -> bool:
        """Submit one signed approval toward quorum.

        Verifies approval belongs to policy, validates signature via reused verifier (P3),
        and consumes single-use approval token via ReplayStore (FR-8.2).
        """
        if self._finalized:
            return False

        if approval.policy_id != self._policy.policy_id:
            return False

        if approval.key_id in self._approved_keys:
            return False

        # Verify signature using injected verifier (e.g. SignatureCombiner)
        try:
            valid = self._verifier.verify(approval.signature, approval.message)
            if not valid:
                return False
        except Exception:
            return False

        # Ensure this approval has not been consumed previously (ReplayStore)
        replay_key = f"threshold_approval:{approval.policy_id}:{approval.key_id}"
        if not self._replay_store.consume_once(replay_key):
            return False

        self._approved_keys.add(approval.key_id)
        return True

    def finalize(self) -> bool:
        """Finalize the threshold decision once quorum is reached.

        Executes only once quorum is met, and can execute exactly once (FR-8.2).
        Subsequent calls return False without re-triggering the gated action.
        """
        if self._finalized:
            return False

        if not self.is_quorum_reached:
            return False

        self._finalized = True
        if self._action is not None:
            self._action()
        return True
