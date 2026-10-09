# `replay_store.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Defines the `ReplayStore` `Protocol` — one of the eight foundational Layer-0 interfaces every algorithm-agile component above it is built against, never against a concrete implementation directly (P1).

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/interfaces/`
- **Depends on:** nothing — this is a foundational `Protocol`, Layer 0's own contract.
- **Imported by:** `in_memory_replay_store.py` (Layer 0 impl); `challenge_issuer.py`, `session_orchestrator.py` (Layer 4), `push_authenticator.py` (Layer 5), `backup_code_manager.py` (Layer 6-7)

## Docstring contract
- **Layer:** 0
- **Depends on:** Nothing internal.
- **Implements:** `consume_once(token: str) -> bool` — returns `True` on first consumption, `False` (or raises `ReplayDetectedError`, per the concrete implementation's documented contract) on any subsequent attempt with the same token
- **Outside:** What counts as a "token" semantically (challenge ID, session token, backup code, push approval) — that's each caller's concern; this interface is content-agnostic.
- **Inside:** Atomic consume-once semantics — check-and-write must not be two separate steps a race can split.
- **Security notes:** FR-4.2 / SR-11 — every replay-sensitive flow (challenge responses, session tokens, backup codes, push-approval tokens) is checked here, not reimplemented ad hoc per component.

## Required behavior
- `ReplayStore` is a `typing.Protocol` defining `consume_once(token) -> bool`.
- FR-4.2: a consumed challenge/token cannot be replayed — `consume_once` semantics apply to every replay-sensitive flow across the whole system, not just Layer 4.
- Consumption must be atomic (write-with-check-in-one-step), not a separate read-then-write, so two concurrent attempts with the same token can't both succeed.

## Inputs / outputs
- **In/Out:** defined per-method by the `Protocol`; see `Docstring contract` above.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-11.** Push/backup-code approvals — and, more generally per FR-4.2, every replay-sensitive credential — are consumed through this interface: single use, no replay.

## Mandatory tests this must pass
- No dedicated test file — a `Protocol` has no behavior of its own to test; conformance is exercised indirectly by every concrete implementation's own test suite.

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any concrete implementation — those live in `impls/`.

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`
