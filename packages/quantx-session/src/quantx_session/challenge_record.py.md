# `challenge_record.py`

**Package:** `quantx-session` · **Layer:** 4 — Session · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The `Challenge` value type stored via `KeyValueStore` — `challenge_id`, `subject_id`, `nonce`, `issued_at`/`expires_at`, and the server-fixed `required_mode` (`07-database-design.md`).

## Part of
- **Depends on:** `quantx_core.types.mode.Mode`, `quantx_core.types.ttl.TTL` (Layer 0)
- **Imported by:** `challenge_issuer.py`, `session_orchestrator.py` (this package)

## Shape
- `challenge_id` — key.
- `subject_id` — who it was issued to.
- `nonce` — random bytes, canonicalized via `JCSCanonicalizer` before signing.
- `issued_at` — from injected `Clock`, never wall-clock read directly (SR-14).
- `expires_at` — TTL-backed.
- `required_mode` — set server-side at issuance; never trusted from a later client message (SR-1).
- Immutable once issued — a challenge's `required_mode` cannot be changed after the fact by anything, including this type's own interface.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- `InMemoryKVStore` hits its `max_entries` cap while storing challenges → SR-3, enforced by the backing store, not this type.

## Non-negotiable principles that apply
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`07-database-design.md`, `10-security-requirements.md`
