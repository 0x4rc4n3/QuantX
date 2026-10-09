# `test_threshold_manager.py`

**Package:** `quantx-threshold` · **Layer:** 8 — Threshold / multi-key policies · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `ThresholdManager.finalize()` executes only once quorum is reached, exactly once, and that it reuses `SignatureCombiner` for approval verification.

## Part of / dependency graph
- **Package:** `quantx-threshold`, `tests/`
- **Depends on:** `threshold_manager.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 8
- **Depends on:** `threshold_manager.py`
- **Implements:** pytest test functions.
- **Outside:** Policy validation — `test_threshold_policy.py`.
- **Inside:** Quorum-gated `finalize()` behavior.
- **Security notes:** Confirms FR-8.2 at the unit level.

## Required behavior
- `finalize()` before quorum is reached is rejected/no-op.
- `finalize()` after quorum succeeds, and a second call has no further effect.
- Each submitted approval is verified via `SignatureCombiner`, not a hand-rolled check.

## Inputs / outputs
- **In:** submitted approvals.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- `finalize()` is called before quorum is reached → rejected/no-op (`13-error-and-edge-cases.md`).

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `threshold_manager.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Policy validation — separate file.

## Source docs
`04-functional-requirements.md`, `13-error-and-edge-cases.md`
