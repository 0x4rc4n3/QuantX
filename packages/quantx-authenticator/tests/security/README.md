# `quantx-authenticator/tests/security/`

## What this is
Layer 5's three security tests: TOTP's rate-limiter independence, SR-5 (push-issuance rate-limited before send), and SR-11 (push-approval replay rejection).

## Part of
`quantx-authenticator`, Layer 5.

## Contains
- `test_totp_rate_limiter_independent_of_session_limiter.py` — FR-5.2
- `test_sr_05_push_issuance_rate_limited_before_send.py` — SR-5
- `test_sr_11_push_approval_replay_rejected.py` — SR-11

## Why divided this way
One descriptively-named file for the foundational FR-5.2 independence property (no single SR number), two `test_sr_<NN>_*`-named files for SR-5 and SR-11, per `14-directory-structure.md`'s convention.

## Dependency rules
- The TOTP independence test depends on both `totp_provider.py` and Layer 4's `session_orchestrator.py` for cross-limiter comparison.
- The SR-5/SR-11 tests depend on `push_authenticator.py` only.

## Source docs
`14-directory-structure.md`, `04-functional-requirements.md`, `10-security-requirements.md`
