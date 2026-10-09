# `push_approval_record.py`

**Package:** `quantx-authenticator` · **Layer:** 5 — Second factor · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The pending/consumed push-approval value type `push_authenticator.py` issues and later consumes via `ReplayStore`.

## Part of
- **Depends on:** `quantx_core.types.ttl.TTL` (Layer 0)
- **Imported by:** `push_authenticator.py` (this package)

## Shape
- `approval_id` — key, consumed via `ReplayStore` (SR-11).
- `subject_id`.
- `issued_at` / `expires_at` — via `Clock`, TTL-backed.
- `consumed` — set exactly once, never re-verifiable after use (mirrors the backup-code record's consume-once shape, `07-database-design.md`).
- Immutable once issued — a `PushApprovalRecord`'s `consumed` state transition happens via `ReplayStore`, not by mutating this value type directly.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A push approval is replayed after consumption → rejected via `ReplayStore` consume-once (SR-11, `13-error-and-edge-cases.md`).

## Non-negotiable principles that apply
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`07-database-design.md`, `10-security-requirements.md`
