# `in_memory_replay_store.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The reference `ReplayStore` implementation, backing Recipe A. Provides atomic consume-once semantics for challenges, session tokens, backup codes, and push approvals.

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/impls/`
- **Depends on:** `quantx_core.interfaces.replay_store.ReplayStore` (Layer 0 interface this implements)
- **Imported by:** `default_setup.py` (Layer 4, Recipe A wiring)

## Docstring contract
- **Layer:** 0
- **Depends on:** `ReplayStore` (the interface it implements)
- **Implements:** InMemoryReplayStore
- **Outside:** Anything not directly part of this one interface's contract.
- **Inside:** The concrete logic satisfying that contract.
- **Security notes:** **SR-11 / FR-4.2.** Consume-once semantics apply to every replay-sensitive flow.

## Required behavior
- Implements `consume_once(token) -> bool` such that a token can be consumed exactly once, atomically.
- Its own consumed-token state goes through an injected `KeyValueStore` rather than a private dict, per FR-0.2/P5 `(inferred: FR-0.2 states no component may hold its own ad hoc dict/cache for anything that must survive across calls; the docs don't spell out InMemoryReplayStore's internal storage mechanism by name, but P5 make a private dict here inconsistent with the architecture)`.

## Inputs / outputs
- **In:** `consume_once(token)`.
- **Out:** `True` on first consumption; on replay, either `False` or a raised `ReplayDetectedError`, per this class's documented contract.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A challenge/token/backup-code/push-approval is replayed → rejected via `ReplayStore` consume-once; second attempt never succeeds, regardless of timing (`13-error-and-edge-cases.md`).

## Security notes
- **SR-11 / FR-4.2.** Consume-once semantics apply to every replay-sensitive flow.

## Mandatory tests this must pass
- `tests/impls/test_in_memory_replay_store.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything beyond the one interface this file implements — reference/dev implementations stay narrowly scoped.

## Source docs
`07-database-design.md`, `06-system-architecture.md`, `04-functional-requirements.md`
