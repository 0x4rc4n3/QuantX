"""
Layer: 4
Depends on: Every Layer 0-4 component Recipe A composes.
Implements: default_setup() -> tuple[ChallengeIssuer, SessionOrchestrator, AlgorithmRegistry]
Outside: Recipe B/C wiring — those are client-specific compositions, not this file's job.
Inside: Constructing the full in-memory Recipe-A object graph in one call.
Security notes: Uses allow_unsigned=True for the registry — appropriate for Recipe A only, never a pattern to copy for Recipe B/C (FR-3.3).
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.impls.system_clock import SystemClock
from quantx_core.interfaces.clock import Clock
from quantx_core.interfaces.verifier import Verifier
from quantx_core.types.mode import Mode
from quantx_registry.algorithm_registry import AlgorithmRegistry

from quantx_session.challenge_issuer import ChallengeIssuer
from quantx_session.session_orchestrator import SessionOrchestrator


def default_setup(
    config_path: Path | str | None = None,
    custom_clock: Clock | None = None,
    custom_verifiers_by_role: Mapping[str, Mapping[str, Verifier]] | None = None,
) -> tuple[ChallengeIssuer, SessionOrchestrator, AlgorithmRegistry]:
    """
    Recipe A setup helper: in-memory state, unsigned dev registry config, system clock,
    canonicalizer, challenge issuer, and session orchestrator ready for immediate end-to-end demo.
    """
    clock = custom_clock or SystemClock()
    kv_store = InMemoryKVStore(clock=clock, max_entries=1000)
    replay_store = InMemoryReplayStore(kv_store=kv_store)
    identity_rate_limiter = InMemoryRateLimiter(
        kv_store=kv_store, clock=clock, limit=10, window_seconds=60
    )
    global_rate_limiter = InMemoryRateLimiter(
        kv_store=kv_store, clock=clock, limit=100, window_seconds=60
    )
    canonicalizer = JCSCanonicalizer()

    if config_path is None:
        # Default to algorithm_registry.example.yaml in quantx-registry package
        actual_repo_root = Path(__file__).resolve().parents[3]  # packages
        config_path = (
            actual_repo_root / "quantx-registry" / "config" / "algorithm_registry.example.yaml"
        )

    registry = AlgorithmRegistry(config_path=config_path, allow_unsigned=True)

    role_modes: dict[str, Mode] = {}
    combiners_by_role: dict[str, Verifier] = {}

    for role_id, role in registry.roles.items():
        role_modes[role_id] = role.required_mode
        c_verifiers = custom_verifiers_by_role.get(role_id) if custom_verifiers_by_role else None
        sig_comb, _, _ = registry.resolve(role_id, custom_verifiers=c_verifiers)
        combiners_by_role[role_id] = sig_comb

    issuer = ChallengeIssuer(
        kv_store=kv_store,
        clock=clock,
        canonicalizer=canonicalizer,
        role_modes=role_modes,
    )

    orchestrator = SessionOrchestrator(
        kv_store=kv_store,
        replay_store=replay_store,
        identity_rate_limiter=identity_rate_limiter,
        global_rate_limiter=global_rate_limiter,
        clock=clock,
        combiners_by_role=combiners_by_role,
        session_ttl_seconds=3600,
    )

    return issuer, orchestrator, registry
