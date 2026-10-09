# `approval_record.py`

**Package:** `quantx-threshold` · **Layer:** 8 — Threshold / multi-key policies · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The value type representing one submitted approval toward a `ThresholdPolicy`'s quorum.

## Part of
- **Depends on:** `quantx_core.types.algorithm_id.AlgorithmId` (Layer 0)
- **Imported by:** `threshold_manager.py` (this package)

## Shape
- `policy_id` — which `ThresholdPolicy` this approval counts toward.
- `key_id` (`AlgorithmId`-tagged) — which of the policy's keys signed.
- `signature` — the raw signature bytes, verified via the reused `SignatureCombiner`.
- Immutable once submitted — an approval's contribution toward quorum is fixed at submission time.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`04-functional-requirements.md`
