"""Unit tests for ThresholdManager quorum tracking and finalization.

Layer: 8
Depends on: quantx_core.impls.in_memory_replay_store.InMemoryReplayStore, quantx_core.types.algorithm_id.AlgorithmId, quantx_threshold.approval_record.ApprovalRecord, quantx_threshold.threshold_manager.ThresholdManager, quantx_threshold.threshold_policy.ThresholdPolicy
Implements: Pytest tests validating quorum progress and single-shot finalize execution
Outside: Policy construction validation
Inside: Approval submission, signature verification, quorum gate check, and single-shot finalization
Security notes: Confirms FR-8.2: finalize() executes only once quorum is met, exactly once.
"""

from __future__ import annotations

from conftest import MockVerifier
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.types.algorithm_id import AlgorithmId
from quantx_threshold.approval_record import ApprovalRecord
from quantx_threshold.threshold_manager import ThresholdManager
from quantx_threshold.threshold_policy import ThresholdPolicy


def test_threshold_manager_quorum_and_finalize_lifecycle(
    valid_policy: ThresholdPolicy,
    replay_store: InMemoryReplayStore,
    mock_verifier: MockVerifier,
) -> None:
    action_called = False

    def on_finalize() -> None:
        nonlocal action_called
        action_called = True

    manager = ThresholdManager(
        policy=valid_policy,
        verifier=mock_verifier,
        replay_store=replay_store,
        action=on_finalize,
    )

    # 1. Finalize before quorum fails
    assert manager.is_quorum_reached is False
    assert manager.finalize() is False
    assert action_called is False

    # 2. Submit first approval (1 of 2 required)
    app1 = ApprovalRecord(
        policy_id="board-approval-policy",
        key_id="director-1",
        algorithm=AlgorithmId.ED25519,
        signature=b"valid-signature",
        message=b"approve-wire-transfer",
    )
    assert manager.submit_approval(app1) is True
    assert manager.approved_count == 1
    assert manager.is_quorum_reached is False
    assert manager.finalize() is False
    assert action_called is False

    # 3. Submitting duplicate approval for same key fails
    assert manager.submit_approval(app1) is False

    # 4. Submitting invalid signature fails
    app_invalid = ApprovalRecord(
        policy_id="board-approval-policy",
        key_id="director-2",
        algorithm=AlgorithmId.ED25519,
        signature=b"bad-signature",
        message=b"approve-wire-transfer",
    )
    assert manager.submit_approval(app_invalid) is False
    assert manager.approved_count == 1

    # 5. Submit second valid approval (2 of 2: quorum reached)
    app2 = ApprovalRecord(
        policy_id="board-approval-policy",
        key_id="director-2",
        algorithm=AlgorithmId.ED25519,
        signature=b"valid-signature",
        message=b"approve-wire-transfer",
    )
    assert manager.submit_approval(app2) is True
    assert manager.approved_count == 2
    assert manager.is_quorum_reached is True

    # 6. Finalize executes action exactly once
    assert manager.finalize() is True
    assert action_called is True
    assert manager.is_finalized is True

    # 7. Subsequent finalize call is a no-op (returns False)
    action_called = False
    assert manager.finalize() is False
    assert action_called is False
