# `clock.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Defines the `Clock` `Protocol` — one of the eight foundational Layer-0 interfaces every algorithm-agile component above it is built against, never against a concrete implementation directly (P1).

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/interfaces/`
- **Depends on:** nothing — this is a foundational `Protocol`, Layer 0's own contract.
- **Imported by:** `system_clock.py` (Layer 0, the production implementation); `challenge_issuer.py`, `session_orchestrator.py` (Layer 4), `in_memory_replay_store.py`, `in_memory_rate_limiter.py` (Layer 0 impls), `totp_provider.py`/`push_authenticator.py` (Layer 5) — every timestamp-consuming component

## Docstring contract
- **Layer:** 0
- **Depends on:** Nothing internal.
- **Implements:** `now() -> datetime` (or equivalent timestamp type)
- **Outside:** Any TTL/expiry math — that's each caller's job using the value this returns.
- **Inside:** The single method that must be the only path to the current time in the entire codebase.
- **Security notes:** FR-0.3 / SR-14 — `Clock` is always injected; no component reads wall-clock time directly and no component uses an `x or default` pattern on a timestamp.

## Required behavior
- `Clock` is a `typing.Protocol` defining `now()`.
- FR-0.3: no component reads wall-clock time directly, and no component uses an `x or default` pattern on a timestamp — every timestamp-consuming component takes a `Clock` in its constructor and calls `.now()` on it.

## Inputs / outputs
- **In/Out:** defined per-method by the `Protocol`; see `Docstring contract` above.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-14.** Timestamps come only from an injected `Clock`, never `or`-defaulted against a wall-clock read — this matters because a component that silently falls back to `datetime.now()` when a value is falsy defeats deterministic testing of expiry logic and can mask clock-skew attacks in a way that's hard to catch in review.

## Mandatory tests this must pass
- No dedicated test file — a `Protocol` has no behavior of its own to test; conformance is exercised indirectly by every concrete implementation's own test suite.

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any concrete implementation — those live in `impls/`.

## Source docs
`10-security-requirements.md`, `06-system-architecture.md`, `04-functional-requirements.md`
