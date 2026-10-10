"""End-to-end security test for SR-3: In-memory store hard max_entries cap holds across system.

Layer: cross-cutting
Depends on: quantx_core.impls.in_memory_kv_store.InMemoryKVStore, quantx_session.challenge_issuer.ChallengeIssuer, quantx_core.exceptions.BackendUnavailableError
Implements: Mandatory full-stack end-to-end test for SR-3 (in-memory store hard max_entries cap)
Outside: Every other numbered SR item
Inside: Drive the full wired system until store capacity is reached, confirming hard cap trips holistically
Wire format: Native storage structures
Security notes: Mandatory SR-3 end-to-end confirmation across quantx-core and quantx-session
"""

from __future__ import annotations

import pytest
from quantx_core.exceptions import BackendUnavailableError
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.impls.system_clock import SystemClock
from quantx_core.types.mode import Mode
from quantx_session.challenge_issuer import ChallengeIssuer


def test_sr_03_end_to_end_kv_store_cap_trips() -> None:
    clock = SystemClock()
    # Construct an in-memory store capped at 5 entries
    capped_store = InMemoryKVStore(clock=clock, max_entries=5)
    canonicalizer = JCSCanonicalizer()

    issuer = ChallengeIssuer(
        kv_store=capped_store,
        clock=clock,
        canonicalizer=canonicalizer,
        role_modes={"session-auth": Mode.HYBRID},
    )

    # Issue 5 challenges successfully to fill store
    for i in range(5):
        issuer.issue(role_id="session-auth", subject_id=f"user-{i}@corp.internal")

    # The 6th challenge must fail due to the hard cap
    with pytest.raises(BackendUnavailableError, match="limit reached"):
        issuer.issue(role_id="session-auth", subject_id="overflow@corp.internal")
