# `hotp_provider.py`

**Package:** `quantx-authenticator` · **Layer:** 5 — Second factor · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies offline HOTP (counter-based) codes, alongside `totp_provider.py`'s time-based verification, as the same class of additional required gate (D4, FR-5.1).

## Part of / dependency graph
- **Package:** `quantx-authenticator`, `src/quantx_authenticator`
- **Depends on:** `quantx_core.interfaces.rate_limiter.RateLimiter` (Layer 0, its own independent instance); `quantx_wallet.KeyWallet` (Layer 6, for durable secret and counter storage, per D11)
- **Imported by:** `session_orchestrator.py` (Layer 4, as an additional configured gate, alternative to or alongside TOTP)

## Docstring contract
- **Layer:** 5
- **Depends on:** `RateLimiter` (Layer 0); `KeyWallet` (Layer 6, once it exists, per D11)
- **Implements:** `verify(subject_id, code) -> bool`
- **Outside:** Time-based verification — `totp_provider.py`'s job.
- **Inside:** HOTP code verification and counter increment on success.
- **Security notes:** Rate limiting mirrors `totp_provider.py`: an independent `RateLimiter` instance, lockout thresholds from config (D-015).

## Required behavior
- Verifies HOTP codes against a stored counter, incrementing the counter on each successful verify (`07-database-design.md`'s TOTP/HOTP secret entity: `counter (HOTP only)` — incremented on each successful verify).
- Integrates into `SessionOrchestrator` as an additional required gate, same as `totp_provider.py` (FR-5.1).
- Secret (and counter) storage is wired through `KeyWallet` as soon as Layer 6 exists (D11) — no interim `KeyValueStore`-backed store.

## Inputs / outputs
- **In:** `subject_id`, an HOTP code.
- **Out:** `bool`; on success, the stored counter increments.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Look-ahead window of 10 counters; the counter advances only after a successful verification; a failed code never advances it (D-015).

## Security notes
- **D11 / FR-5.4.** No interim secret store.
- Independent rate-limiting discipline, mirroring FR-5.2's requirement for TOTP.

## Mandatory tests this must pass
- `tests/test_hotp_provider.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.

## Explicitly out of scope for this file
- Time-based verification — `totp_provider.py`.

## Source docs
`07-database-design.md`, `00-index.md`, `04-functional-requirements.md`
