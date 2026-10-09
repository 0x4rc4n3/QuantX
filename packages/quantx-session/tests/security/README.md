# `quantx-session/tests/security/`

## What this is
Layer 4's two security tests: SR-10 (mint-ordering) and the foundational replay/rate-limit rejection test.

## Part of
`quantx-session`, Layer 4.

## Contains
- `test_sr_10_token_never_minted_before_all_gates_pass.py` — SR-10
- `test_replay_and_rate_limit_rejection.py` — FR-4.2 / FR-4.4, foundational, no single SR number

## Why divided this way
One file named `test_sr_<NN>_*` for the numbered SR item, one descriptively-named file for the foundational, cross-cutting replay/rate-limit behavior — per `14-directory-structure.md`'s stated naming convention and its exception.

## Dependency rules
- Both depend on `session_orchestrator.py`; the replay test also depends on `ReplayStore`/`RateLimiter` (Layer 0).

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`
