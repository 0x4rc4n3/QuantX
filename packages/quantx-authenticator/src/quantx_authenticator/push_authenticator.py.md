# `push_authenticator.py`

**Package:** `quantx-authenticator` · **Layer:** 5 — Second factor · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Issues and verifies push-notification approvals as a second factor — rate-limited before sending (SR-5) and consumed through `ReplayStore` so an approval cannot be replayed (SR-11).

## Part of / dependency graph
- **Package:** `quantx-authenticator`, `src/quantx_authenticator`
- **Depends on:** `quantx_core.interfaces.rate_limiter.RateLimiter` (Layer 0, its own independent instance, gating issuance specifically — SR-5); `quantx_core.interfaces.replay_store.ReplayStore` (Layer 0, consuming approvals — SR-11); `push_approval_record.py` (this package)
- **Imported by:** `session_orchestrator.py` (Layer 4, as an additional configured gate)

## Docstring contract
- **Layer:** 5
- **Depends on:** `RateLimiter`, `ReplayStore` (Layer 0); `PushApprovalRecord` (this package)
- **Implements:** `issue(subject_id) -> PushApprovalRecord`; `consume(approval_id) -> bool`
- **Outside:** Actually delivering the push notification over a specific push provider/transport `(inferred: the docs specify issuance rate-limiting and consume-once semantics, not the transport integration itself)`.
- **Inside:** Issuance rate-limiting and consume-once verification.
- **Security notes:** SR-5 (rate-limited before send) and SR-11 (consumed via `ReplayStore`) in full.

## Required behavior
- Gates challenge issuance behind a rate limiter **before** sending a push (SR-5) — the limiter check happens prior to any send attempt, not after.
- Consumes approvals through `ReplayStore` so a push approval cannot be replayed (FR-5.3, SR-11).
- Push-issuance rate limiting uses its own independent limiter instance, separate from Layer 4's session limiter and from TOTP's (`07-database-design.md`'s rate-limit-counter entity: "a separate one for ... push-issuance").

## Inputs / outputs
- **In:** `issue`: `subject_id`. `consume`: `approval_id`.
- **Out:** `issue`: a `PushApprovalRecord` (only after the rate-limit check passes). `consume`: `bool`, single-use.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Push approval latency is an observability metric, not a correctness requirement of this file (`12-analytics-and-events.md`) — noted here only so it isn't mistaken for a behavioral spec of this class.

## Security notes
- **SR-5.** Rate-limited before sending, not just at verification.
- **SR-11.** Consume-once via `ReplayStore`.

## Mandatory tests this must pass
- `tests/test_push_authenticator.py`
- `tests/security/test_sr_05_push_issuance_rate_limited_before_send.py`
- `tests/security/test_sr_11_push_approval_replay_rejected.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.

## Explicitly out of scope for this file
- The actual push-delivery transport integration.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `07-database-design.md`, `12-analytics-and-events.md`
