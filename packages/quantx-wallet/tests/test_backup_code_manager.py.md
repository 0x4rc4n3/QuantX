# `test_backup_code_manager.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `BackupCodeManager.verify()` accepts a genuine, unconsumed code exactly once.

## Part of / dependency graph
- **Package:** `quantx-wallet`, `tests/`
- **Depends on:** `backup_code_manager.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 6-7
- **Depends on:** `backup_code_manager.py`
- **Implements:** pytest test functions.
- **Outside:** The SR-11 replay-rejection adversarial scenario — separate file.
- **Inside:** Genuine single-use verification.
- **Security notes:** Confirms FR-6.4 at the unit level.

## Required behavior
- A genuine, unconsumed code verifies successfully exactly once.

## Inputs / outputs
- **In:** a backup code.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the non-adversarial unit test for `backup_code_manager.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- SR-11 replay-rejection — separate file.

## Source docs
`04-functional-requirements.md`
