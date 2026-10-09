# `threshold_manager.py`

**Package:** `quantx-threshold` · **Layer:** 8 — Threshold / multi-key policies · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`'s review gates).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/threshold_policy_and_manager.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
Tracks approvals toward a `ThresholdPolicy`'s quorum and executes `finalize()` exactly once quorum is met — reuses `SignatureCombiner` for the actual cryptographic verification of each approval rather than reimplementing verification logic (FR-8.2, P3).

## Part of / dependency graph
- **Package:** `quantx-threshold`, `src/quantx_threshold`
- **Depends on:** `threshold_policy.py` (this package); `signature_combiner.py` (Layer 2, reused for verifying each approval — never a second, separate verification path); `quantx_core.interfaces.replay_store.ReplayStore` (Layer 0, so an approval can't be counted toward quorum twice)
- **Imported by:** `approval_record.py` consumers; integrating-application multi-key approval flows

## Docstring contract
- **Layer:** 8
- **Depends on:** `ThresholdPolicy` (this package); `SignatureCombiner` (Layer 2, reused, P3); `ReplayStore` (Layer 0)
- **Implements:** `submit_approval(approval) -> None`; `finalize() -> bool`
- **Outside:** Defining what a valid policy is — `threshold_policy.py`'s job.
- **Inside:** Approval tracking and the exactly-once `finalize()` execution.
- **Security notes:** FR-8.2: `finalize()` executes only once quorum is met, and does so exactly once — never re-triggerable after the fact for the same policy instance.

## Required behavior
- `finalize()` executes only once quorum (`m` valid, distinct approvals) is met (FR-8.2).
- Reuses `SignatureCombiner` for verifying each individual approval — never a second, hand-rolled verification path (P3).
- Each approval is checked against `ReplayStore` so the same approval can't be counted toward quorum more than once.

## Inputs / outputs
- **In:** `submit_approval`: a signed approval from one of the policy's keys. `finalize`: none.
- **Out:** `submit_approval`: none (updates internal quorum-tracking state). `finalize`: `bool`/result, only once quorum is met; a release blocker if it's ever callable twice for the same policy instance with effect the second time.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- `finalize()` is called before quorum is reached → rejected/no-op — never executes early (`13-error-and-edge-cases.md`'s general principle about premature-completion gates, applied here by FR-8.2).

## Security notes
- **FR-8.2.** `finalize()` executes exactly once, only after quorum.

## Mandatory tests this must pass
- `tests/test_threshold_manager.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P3.** Exactly one `SignatureCombiner`, one `KEMCombiner` — pairing is runtime wiring, not a new class.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Defining what a valid policy is — `threshold_policy.py`.
- The underlying signature-verification algorithm — Layer 1/2.

## Source docs
`04-functional-requirements.md`, `13-error-and-edge-cases.md`
