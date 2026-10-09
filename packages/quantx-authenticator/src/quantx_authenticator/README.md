# `quantx_authenticator` — package source root

## What this is
Layer 5: TOTP, HOTP, and push-based second factors, each an additional required gate in `SessionOrchestrator`, never a replacement for the primary factor.

## Part of
`quantx-authenticator`, Layer 5.

## Contains
- `totp_provider.py` — time-based OTP verification
- `hotp_provider.py` — counter-based OTP verification
- `push_authenticator.py` — push-notification approval issuance/consumption
- `push_approval_record.py` — pending/consumed push-approval value type

## Why divided this way
Three independent second-factor mechanisms, each with its own rate-limiting/replay surface, kept in separate files per `14-directory-structure.md`'s atomicity rule.

## Dependency rules
- None of these three providers import each other.
- Each has its own independent `RateLimiter` instance (FR-5.2, SR-5) — none share state with Layer 4's session limiter or with each other.
- Durable secret storage for TOTP/HOTP is deferred to `KeyWallet` (Layer 6) per D11 — this package does not build an interim secret store.

## Source docs
`06-system-architecture.md`, `00-index.md`, `04-functional-requirements.md`
