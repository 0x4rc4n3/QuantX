# `ttl.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
A value type wrapping a time-to-live duration, used everywhere something in `KeyValueStore` (challenges, session tokens, rate-limit windows) needs an expiry that is computed through the injected `Clock`, never a raw wall-clock delta.

## Part of
- **Depends on:** nothing internal to QuantX (foundational value type).
- **Imported by:** `challenge_issuer.py`, `session_orchestrator.py` (Layer 4) for challenge/token expiry; `in_memory_kv_store.py`, `redis_kv_store.py` (Layer 0 impls) as the `ttl` parameter shape

## Shape
- `TTL` — a small frozen value type wrapping a duration (e.g. seconds), used as the optional `ttl` parameter on `KeyValueStore.set()`.
- Immutable once constructed.
- Expiry math (`issued_at + ttl` → `expires_at`) is performed by the caller using an injected `Clock`, never by this type reading time itself (SR-14) `(inferred: this file defines the duration shape; the docs don't spell out whether expiry-math is a method on TTL or done by the caller, but SR-14 rules out this type reading wall-clock time internally either way)`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`10-security-requirements.md`, `07-database-design.md`, `04-functional-requirements.md`
