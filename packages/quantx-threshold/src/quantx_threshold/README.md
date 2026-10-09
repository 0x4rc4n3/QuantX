# `quantx_threshold` — package source root

## What this is
Layer 8: m-of-n threshold/multi-key policies, built by reusing `SignatureCombiner` rather than reimplementing verification (P3).

## Part of
`quantx-threshold`, Layer 8. `threshold_policy.py` and `threshold_manager.py` are both `GATE_REVIEW_REQUIRED`.

## Contains
- `threshold_policy.py` — m-of-n policy definition, duplicate-key rejection (SR-12)
- `threshold_manager.py` — approval tracking, exactly-once `finalize()`
- `approval_record.py` — one submitted approval, value type

## Why divided this way
Policy definition (what's valid) and runtime approval tracking (what's happened so far) are independently testable concerns, per `14-directory-structure.md`'s atomicity rule.

## Dependency rules
- `threshold_manager.py` reuses `SignatureCombiner` (Layer 2) rather than reimplementing signature verification — the whole point of P3.
- `threshold_policy.py` has no dependency on `threshold_manager.py` — a policy is a value that can be validated independent of any runtime tracking.

## Source docs
`04-functional-requirements.md`, `14-directory-structure.md`
