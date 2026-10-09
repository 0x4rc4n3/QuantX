# `threshold_policy.py`

**Package:** `quantx-threshold` · **Layer:** 8 — Threshold / multi-key policies · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`, SR-12).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/threshold_policy_and_manager.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
Defines an m-of-n threshold policy over a set of keys — rejects duplicate keys at policy creation, not at use (FR-8.1, SR-12), so a degenerate policy (the same key counted twice toward quorum) can never exist.

## Part of / dependency graph
- **Package:** `quantx-threshold`, `src/quantx_threshold`
- **Depends on:** `quantx_core.types.algorithm_id.AlgorithmId` (Layer 0, keys are identified per-algorithm)
- **Imported by:** `threshold_manager.py` (this package)

## Docstring contract
- **Layer:** 8
- **Depends on:** `AlgorithmId` (Layer 0)
- **Implements:** `ThresholdPolicy(keys, m) -> ThresholdPolicy` — constructor validates and rejects duplicates
- **Outside:** Tracking approvals toward quorum at runtime — `threshold_manager.py`'s job entirely.
- **Inside:** Policy definition and validation, at construction time only.
- **Security notes:** SR-12 in full: duplicate-key rejection happens here, at creation, so it can never be bypassed downstream by `threshold_manager.py` forgetting to check.

## Required behavior
- Rejects duplicate keys at policy creation (FR-8.1, SR-12) — the constructor validates the full key set up front; there is no code path that constructs a `ThresholdPolicy` with a repeated key.
- Stores `m` (the quorum threshold) and the validated key set as immutable policy state.

## Inputs / outputs
- **In:** a set of keys (as `AlgorithmId`-tagged public keys) and `m` (quorum threshold).
- **Out:** a validated `ThresholdPolicy`, or a rejection at construction time if any key is duplicated or `m` is out of range (e.g. `m > n`) `(inferred: the docs specify duplicate-key rejection explicitly; an m > n bound check is an obvious corollary the docs don't spell out by name)`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A threshold policy is constructed with a duplicate key → rejected at creation, not at use (SR-12, `13-error-and-edge-cases.md`).

## Security notes
- **SR-12.** Duplicate keys rejected at policy creation, never deferred to use time.

## Mandatory tests this must pass
- `tests/test_threshold_policy.py`
- `tests/security/test_sr_12_duplicate_key_rejected_at_policy_creation.py`

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Tracking approvals at runtime — `threshold_manager.py`.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
