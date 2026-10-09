# `key_value_store.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Defines the `KeyValueStore` `Protocol` — one of the eight foundational Layer-0 interfaces every algorithm-agile component above it is built against, never against a concrete implementation directly (P1).

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/interfaces/`
- **Depends on:** nothing — this is a foundational `Protocol`, Layer 0's own contract.
- **Imported by:** `in_memory_kv_store.py`, `redis_kv_store.py` (Layer 0 impls); `challenge_issuer.py`, `session_orchestrator.py` (Layer 4) and, per FR-0.2, any other stateful component

## Docstring contract
- **Layer:** 0
- **Depends on:** Nothing internal.
- **Implements:** `get(key: str) -> bytes | None`; `set(key: str, value: bytes, ttl: TTL | None = None) -> None`; `delete(key: str) -> None`
- **Outside:** Replay/rate-limit semantics — those are separate `ReplayStore`/`RateLimiter` interfaces layered on top, not folded into this one.
- **Inside:** The generic get/set/delete/TTL contract every stateful component persists through.
- **Security notes:** FR-0.2 — the single approved path for anything stateful; no component may hold its own ad hoc dict/cache for anything that must survive across calls.

## Required behavior
- `KeyValueStore` is a `typing.Protocol` defining `get`, `set` (with optional `TTL`), and `delete`.
- FR-0.2: every stateful component's persistence goes through this interface — `ChallengeIssuer`, `SessionOrchestrator`, and the reference `ReplayStore`/`RateLimiter` implementations all take a `KeyValueStore` in their constructor rather than holding their own dict/cache.

## Inputs / outputs
- **In/Out:** defined per-method by the `Protocol`; see `Docstring contract` above.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- FR-0.2 — the single approved path for anything stateful; no component may hold its own ad hoc dict/cache for anything that must survive across calls.

## Mandatory tests this must pass
- No dedicated test file for the Protocol itself — see `test_in_memory_kv_store.py` and `test_redis_kv_store.py` for the two concrete implementations.

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any concrete implementation — those live in `impls/`.

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`
