# `session_orchestrator.py`

**Package:** `quantx-session` · **Layer:** 4 — Session · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The central orchestrator gating primary-factor verification, optional Layer-5 second factors, replay/rate-limit checks, and session-token minting — the `finish()`/`validate()` halves of the end-to-end demo flow, and the single place SR-10 is enforced.

## Part of / dependency graph
- **Package:** `quantx-session`, `src/quantx_session`
- **Depends on:** `SignatureCombiner`/`KEMCombiner` (Layer 2, via `AlgorithmRegistry`); `quantx_core.interfaces.replay_store.ReplayStore`, `quantx_core.interfaces.rate_limiter.RateLimiter`, `quantx_core.interfaces.clock.Clock`, `quantx_core.interfaces.key_value_store.KeyValueStore` (Layer 0); `challenge_record.py`, `session_token.py` (this package); `totp_provider.py` (Layer 5, optional additional gate, wired in once configured — not a hard dependency of this file itself)
- **Imported by:** `default_setup.py` (this package); `service/src/quantx_service/routers/verify_router.py`, `.../session_router.py`

## Docstring contract
- **Layer:** 4
- **Depends on:** `SignatureCombiner`/`KEMCombiner` (Layer 2), `ReplayStore`, `RateLimiter`, `Clock`, `KeyValueStore` (Layer 0); optionally `TotpProvider`/`PushAuthenticator` (Layer 5) as additional configured gates
- **Implements:** `finish(challenge_id, signed_response) -> SessionToken`; `validate(token) -> bool`
- **Outside:** The actual cryptographic verification logic — delegates entirely to `SignatureCombiner`/`KEMCombiner`; TOTP/push verification logic itself — delegates to Layer 5.
- **Inside:** Gate sequencing: primary factor → configured second factors → replay check → rate limit → token minting, in that order, with no early token creation.
- **Security notes:** SR-10 in full: token minted only as the final statement after every required gate passes.

## Required behavior
- Mints a session token only as the last statement after every required gate has passed — no exception path may leave a live token behind (FR-4.3, SR-10).
- Both a per-identity and a global `RateLimiter` gate verification (FR-4.4), as two independently-constructed instances.
- A consumed challenge/token cannot be replayed — `ReplayStore.consume_once` semantics apply (FR-4.2).
- If Layer 5 (TOTP/push) is configured, it's an additional required gate, not a replacement path for the primary factor (FR-5.1) — `factors_completed` is only fully populated once every configured gate, primary and second-factor, has passed.
- `required_mode` used for primary-factor verification comes from the `AlgorithmRegistry` role this orchestrator was constructed against — never from anything in `signed_response` (SR-1).

## Inputs / outputs
- **In:** `finish`: `challenge_id`, `signed_response` (bytes). `validate`: a `SessionToken`.
- **Out:** `finish`: a `SessionToken` on full success, or a rejection (never a live token) on any gate failure. `validate`: `bool`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A session token is requested before all configured factors (primary + Layer 5 if configured) have passed → never issued — token minting is the literal last statement after every gate passes, with no exception path that leaves a live token behind (SR-10, `13-error-and-edge-cases.md`).
- A subject exceeds their per-identity rate limit → `429`-equivalent rejection, independent of the global limiter's state.
- Global rate limit is exceeded even though no single identity is over their own limit → still rejected — the two limiters are independent gates.
- A challenge/token is replayed → rejected via `ReplayStore` consume-once; second attempt never succeeds, regardless of timing.

## Security notes
- **SR-10.** This file's central guarantee — mint-last, no exception path leaves a live token behind.
- **SR-1 (verification side).** `required_mode` for primary-factor verification is fixed at construction/registry-resolution time, never from `signed_response`.
- **FR-4.2 / FR-4.4.** Replay and independent per-identity/global rate limiting both gate this flow.

## Mandatory tests this must pass
- `tests/test_session_orchestrator.py`
- `tests/security/test_sr_10_token_never_minted_before_all_gates_pass.py`
- `tests/security/test_replay_and_rate_limit_rejection.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- The actual signature/KEM verification math — Layer 2.
- TOTP/push verification logic itself — Layer 5.
- Choosing algorithms/`required_mode` — Layer 3.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`, `07-database-design.md`, `03-user-stories-and-flows.md`, `09-auth-and-authorization.md`
