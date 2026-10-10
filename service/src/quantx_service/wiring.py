"""Composition root for QuantX REST sidecar.

Layer: sidecar
Depends on: quantx_service.config.ServiceConfig, quantx_registry.algorithm_registry.AlgorithmRegistry, quantx_session.session_orchestrator.SessionOrchestrator
Implements: build_app_dependencies(config) -> AppDependencies and FastAPI dependency injection helpers
Outside: Request routing and HTTP parsing (handled by routers)
Inside: One-time assembly of backends, cryptographic registry, challenge issuer, and session orchestrator
Security notes: Slices and wires configured backends without allowing weaker fallback configurations per CFG-3 and P1.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.impls.redis_kv_store import RedisKVStore
from quantx_core.impls.system_clock import SystemClock
from quantx_core.interfaces.clock import Clock
from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.interfaces.rate_limiter import RateLimiter
from quantx_core.interfaces.replay_store import ReplayStore
from quantx_core.interfaces.verifier import Verifier
from quantx_core.types.mode import Mode
from quantx_registry.algorithm_registry import AlgorithmRegistry
from quantx_session.challenge_issuer import ChallengeIssuer
from quantx_session.challenge_record import ChallengeRecord
from quantx_session.session_orchestrator import SessionOrchestrator
from quantx_session.session_token import SessionToken

from quantx_service.config import ServiceConfig, resolve_secret_ref

__all__ = [
    "AppDependencies",
    "ChallengeIssuer",
    "ChallengeRecord",
    "SessionOrchestrator",
    "SessionToken",
    "build_app_dependencies",
    "get_config",
    "get_dependencies",
    "get_issuer",
    "get_orchestrator",
    "get_registry",
    "set_global_dependencies",
]


@dataclass
class AppDependencies:
    """Container holding wired application dependencies."""

    config: ServiceConfig
    kv_store: KeyValueStore
    clock: Clock
    canonicalizer: JCSCanonicalizer
    replay_store: ReplayStore
    rate_limiter: RateLimiter
    registry: AlgorithmRegistry
    issuer: ChallengeIssuer
    orchestrator: SessionOrchestrator


_GLOBAL_DEPENDENCIES: AppDependencies | None = None


def set_global_dependencies(deps: AppDependencies) -> None:
    """Set the globally configured application dependencies."""
    global _GLOBAL_DEPENDENCIES
    _GLOBAL_DEPENDENCIES = deps


def get_dependencies() -> AppDependencies:
    """FastAPI dependency provider returning active AppDependencies."""
    if _GLOBAL_DEPENDENCIES is None:
        raise RuntimeError("Application dependencies have not been initialized")
    return _GLOBAL_DEPENDENCIES


def get_issuer() -> ChallengeIssuer:
    """FastAPI dependency provider returning the wired ChallengeIssuer."""
    return get_dependencies().issuer


def get_orchestrator() -> SessionOrchestrator:
    """FastAPI dependency provider returning the wired SessionOrchestrator."""
    return get_dependencies().orchestrator


def get_registry() -> AlgorithmRegistry:
    """FastAPI dependency provider returning the wired AlgorithmRegistry."""
    return get_dependencies().registry


def get_config() -> ServiceConfig:
    """FastAPI dependency provider returning the wired ServiceConfig."""
    return get_dependencies().config


def _find_registry_config_path(config: ServiceConfig) -> Path:
    """Locate the YAML config file for AlgorithmRegistry."""
    cfg_opt = config.registry.get("config_path")
    if cfg_opt:
        p = Path(cfg_opt)
        if p.exists():
            return p

    repo_root = Path(__file__).resolve().parents[3]
    candidates = [
        Path("/etc/quantx/algorithm_registry.yaml"),
        repo_root / "packages" / "quantx-registry" / "config" / "algorithm_registry.example.yaml",
        Path.cwd() / "packages" / "quantx-registry" / "config" / "algorithm_registry.example.yaml",
        Path.cwd() / "algorithm_registry.yaml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[1]


def build_app_dependencies(
    config: ServiceConfig,
    custom_clock: Clock | None = None,
    custom_kv_store: KeyValueStore | None = None,
    custom_verifiers_by_role: Mapping[str, Mapping[str, Verifier]] | None = None,
) -> AppDependencies:
    """Construct and assemble all service dependencies from validated configuration."""
    clock = custom_clock or SystemClock()
    canonicalizer = JCSCanonicalizer()

    # 1. State Store
    kv_store: KeyValueStore
    if custom_kv_store is not None:
        kv_store = custom_kv_store
    else:
        state_backend = config.state.get("backend", "memory")
        if state_backend == "redis":
            url_ref = config.state.get("url_ref")
            redis_url = resolve_secret_ref(url_ref) if url_ref else None
            if not redis_url:
                raise ValueError("Redis state backend requires a resolvable url_ref")
            kv_store = RedisKVStore(url=redis_url)
        elif state_backend == "memory":
            kv_store = InMemoryKVStore(clock=clock, max_entries=1000)
        else:
            raise ValueError(f"Unsupported state backend: '{state_backend}'")

    # 2. Replay store and rate limiters
    replay_store = InMemoryReplayStore(kv_store=kv_store, prefix="replay:")
    rate_limiter = InMemoryRateLimiter(
        kv_store=kv_store,
        clock=clock,
        limit=100,
        window_seconds=60,
    )
    global_rate_limiter = InMemoryRateLimiter(
        kv_store=kv_store,
        clock=clock,
        limit=1000,
        window_seconds=60,
    )

    # 3. Algorithm Registry
    allow_unsigned = config.registry.get("config_signing", "unsigned") == "unsigned"
    reg_path = _find_registry_config_path(config)

    registry = AlgorithmRegistry(
        config_path=reg_path,
        allow_unsigned=allow_unsigned,
    )

    role_modes: dict[str, Mode] = {}
    combiners_by_role: dict[str, Verifier] = {}

    for role_id, role in registry.roles.items():
        role_modes[role_id] = role.required_mode
        c_verifiers = custom_verifiers_by_role.get(role_id) if custom_verifiers_by_role else None
        sig_comb, _, _ = registry.resolve(role_id, custom_verifiers=c_verifiers)
        combiners_by_role[role_id] = sig_comb

    # 4. Session Layer
    issuer = ChallengeIssuer(
        kv_store=kv_store,
        clock=clock,
        canonicalizer=canonicalizer,
        role_modes=role_modes,
    )
    orchestrator = SessionOrchestrator(
        kv_store=kv_store,
        replay_store=replay_store,
        identity_rate_limiter=rate_limiter,
        global_rate_limiter=global_rate_limiter,
        clock=clock,
        combiners_by_role=combiners_by_role,
        session_ttl_seconds=3600,
    )

    deps = AppDependencies(
        config=config,
        kv_store=kv_store,
        clock=clock,
        canonicalizer=canonicalizer,
        replay_store=replay_store,
        rate_limiter=rate_limiter,
        registry=registry,
        issuer=issuer,
        orchestrator=orchestrator,
    )
    set_global_dependencies(deps)
    return deps
