# `session_token.py`

**Package:** `quantx-session` · **Layer:** 4 — Session · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The `SessionToken` value type — `token_id`, `subject_id`, `issued_at`/`expires_at`, and `factors_completed`, set only once every required gate has passed (SR-10).

## Part of
- **Depends on:** `quantx_core.types.ttl.TTL` (Layer 0)
- **Imported by:** `session_orchestrator.py` (this package); `service/src/quantx_service/routers/session_router.py`

## Shape
- `token_id` — key.
- `subject_id`.
- `issued_at` / `expires_at` — via `Clock`.
- `factors_completed` — set only once every required gate (incl. Layer 5 second factor, if configured) has passed — never partially populated with a live token attached (SR-10).
- Immutable once minted — a token's `factors_completed` set cannot grow after issuance; a reused/extended-privilege token is not a valid state this type can represent.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A session token is requested before all configured factors have passed → never constructed at all (SR-10) — there is no partially-populated `SessionToken` state.

## Non-negotiable principles that apply
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`07-database-design.md`, `10-security-requirements.md`
