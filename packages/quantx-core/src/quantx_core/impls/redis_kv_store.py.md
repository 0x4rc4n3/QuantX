# `redis_kv_store.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The networked `KeyValueStore` implementation backing Recipe B (production). Swapping this in for `InMemoryKVStore` is the architecture's core falsifiable claim: zero changes to Layers 1-4 (`01-product-requirements.md`).

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/impls/`
- **Depends on:** `quantx_core.interfaces.key_value_store.KeyValueStore` (Layer 0 interface this implements)
- **Imported by:** Recipe-B wiring (client-specific, not part of `default_setup.py`'s Recipe-A path)

## Docstring contract
- **Layer:** 0
- **Depends on:** `KeyValueStore` (the interface it implements)
- **Implements:** RedisKVStore
- **Outside:** Anything not directly part of this one interface's contract.
- **Inside:** The concrete logic satisfying that contract.
- **Security notes:** **SR-4.** Networked backend failure has a stated, implemented fail-closed-vs-degrade decision — never an unhandled exception.

## Required behavior
- Implements `get`/`set`/`delete` from `KeyValueStore` against a Redis (or equivalent) backend, gated behind an optional `redis` extra so `quantx-core` doesn't force the dependency on Recipe-A-only consumers.
- Implements a **stated, explicit fail-closed-vs-degrade decision** on connection failure — raising `BackendUnavailableError` rather than an unhandled exception surfacing as a generic 500 (SR-4) `(inferred: the docs require this decision be made and documented; they don't dictate fail-closed vs. degrade as the specific choice — this file's own docstring is where that decision gets recorded)`.
- TTL passed through to Redis's native expiry where the backend supports it.

## Inputs / outputs
- **In:** `get(key)`, `set(key, value, ttl=None)`, `delete(key)`.
- **Out:** stored bytes or `None`; raises `BackendUnavailableError` on connection failure per the documented fail-closed decision.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Networked backend connection is lost mid-session → a stated, explicit decision (fail-closed vs. degrade) is implemented and documented — not an unhandled exception (SR-4, `13-error-and-edge-cases.md`).
- `KeyValueStore` backend is unreachable at REST-sidecar layer → surfaced as `503 backend_unavailable`, not masked as `401`/`500` (`08-api-specification.md`).

## Security notes
- **SR-4.** Networked backend failure has a stated, implemented fail-closed-vs-degrade decision — never an unhandled exception.

## Mandatory tests this must pass
- `tests/impls/test_redis_kv_store.py`
- `tests/security/test_sr_04_redis_backend_failure_handling.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything beyond the one interface this file implements — reference/dev implementations stay narrowly scoped.

## Source docs
`07-database-design.md`, `05-non-functional-requirements.md`, `06-system-architecture.md`, `04-functional-requirements.md`
