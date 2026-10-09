# `totp_provider.py`

**Package:** `quantx-authenticator` · **Layer:** 5 — Second factor · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies offline TOTP/HOTP codes and integrates into `SessionOrchestrator` as an additional required gate, never a replacement for the primary factor (D4, FR-5.1).

## Part of / dependency graph
- **Package:** `quantx-authenticator`, `src/quantx_authenticator`
- **Depends on:** `quantx_core.interfaces.rate_limiter.RateLimiter` (Layer 0, its own independent instance); `quantx_core.interfaces.clock.Clock` (Layer 0); `quantx_wallet.KeyWallet` (Layer 6, for durable secret storage, wired through per D11 as soon as Layer 6 exists — built against test-fixture secrets until then, per `02-build-order.md` Layer 5's build note)
- **Imported by:** `session_orchestrator.py` (Layer 4, as an additional configured gate)

## Docstring contract
- **Layer:** 5
- **Depends on:** `RateLimiter`, `Clock` (Layer 0); `KeyWallet` (Layer 6, once it exists, per D11)
- **Implements:** `verify(subject_id, code) -> bool`
- **Outside:** Primary-factor verification (Layer 2-4); secret durability before Layer 6 exists (test-fixture secrets used in the interim, per D11/`02-build-order.md`).
- **Inside:** TOTP/HOTP code verification and its own independent rate limiting.
- **Security notes:** FR-5.2: its own rate limiter, independent of the Layer 4 session limiter.

## Required behavior
- Verifies offline TOTP/HOTP codes and integrates into `SessionOrchestrator` as an additional required gate, not a replacement path for the primary factor (FR-5.1).
- Has its own rate limiter, independent of the Layer 4 session limiter (FR-5.2) — brute-force attempts against the TOTP surface trip this limiter without needing the Layer 4 limiter to also be near its own threshold.
- TOTP/HOTP secret storage is wired through Layer 6's `KeyWallet` as soon as it exists (D11) — no interim `KeyValueStore`-backed secret store is built to be thrown away later; verification logic is built now, against test-fixture secrets, per `02-build-order.md`'s Layer-5 build note, and re-wired to `KeyWallet` in the same pass Layer 6 lands.

## Inputs / outputs
- **In:** `subject_id`, a TOTP/HOTP code.
- **Out:** `bool`, plus (independently) a rate-limit rejection if this provider's own limiter has tripped.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Defaults (D-015): RFC 6238, HMAC-SHA1, 6 digits, 30 s step, accept plus or minus one step; each accepted step is consumed through `ReplayStore`, so a code cannot be used twice.

## Security notes
- **FR-5.2.** Independent rate limiter, separate from Layer 4's.
- **D11 / FR-5.4.** No interim secret store — durable storage waits for `KeyWallet`.

## Mandatory tests this must pass
- `tests/test_totp_provider.py`
- `tests/security/test_totp_rate_limiter_independent_of_session_limiter.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.

## Explicitly out of scope for this file
- Primary-factor verification.
- Push-based second factor — `push_authenticator.py`.

## Source docs
`04-functional-requirements.md`, `00-index.md`, `02-build-order.md`, `03-user-stories-and-flows.md`
