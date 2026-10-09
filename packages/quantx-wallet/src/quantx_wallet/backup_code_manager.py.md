# `backup_code_manager.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies each backup code exactly once — a consumed code cannot be reused (FR-6.4), using the same consume-once contract as any other replay-sensitive credential (SR-11).

## Part of / dependency graph
- **Package:** `quantx-wallet`, `src/quantx_wallet`
- **Depends on:** `quantx_core.interfaces.replay_store.ReplayStore` (Layer 0)
- **Imported by:** `session_orchestrator.py` (Layer 4, as a recovery path)

## Docstring contract
- **Layer:** 6-7
- **Depends on:** `ReplayStore` (Layer 0)
- **Implements:** `verify(subject_id, code) -> bool`
- **Outside:** Generating/distributing backup codes to the subject in the first place `(inferred: the docs specify verification/consumption behavior, not the generation-and-delivery flow, which is presumably an integrating-application concern much like identity binding is per 09-auth-and-authorization.md)`.
- **Inside:** Hash comparison and consume-once verification.
- **Security notes:** FR-6.4/SR-11: exactly-once verification via `ReplayStore`.

## Required behavior
- Verifies each code exactly once — a consumed code cannot be reused (FR-6.4).
- Stores/compares `code_hash`, never the raw code, per `07-database-design.md`'s backup-code record shape (`subject_id + code_hash` as key).
- Consumption goes through `ReplayStore`, the same consume-once contract as any other replay-sensitive credential (SR-11).

## Inputs / outputs
- **In:** `subject_id`, a backup code.
- **Out:** `bool`, single-use.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A backup code is reused after consumption → rejected — same consume-once contract as any other replay-sensitive credential (`13-error-and-edge-cases.md`).

## Security notes
- **FR-6.4 / SR-11.**

## Mandatory tests this must pass
- `tests/test_backup_code_manager.py`
- `tests/security/test_sr_11_backup_code_replay_rejected.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.

## Explicitly out of scope for this file
- Generating/distributing codes to the subject.

## Source docs
`04-functional-requirements.md`, `07-database-design.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
