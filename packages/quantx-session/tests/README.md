# `quantx-session` — `tests/`

## What this is
The test suite for Layer 4, including the first true end-to-end demo test in the build order, and the SR-10/replay/rate-limit security tests.

## Part of
`quantx-session`, Layer 4.

## Contains
- `conftest.py` — wired fixtures using real Layer 0-2 components
- `test_challenge_issuer.py`, `test_session_orchestrator.py`
- `test_default_setup_end_to_end_demo.py` — the full demo flow
- `security/` — SR-10 and the replay/rate-limit foundational test

## Why divided this way
Mirrors `src/` per `14-directory-structure.md`.

## Dependency rules
- `test_default_setup_end_to_end_demo.py` is the one test file in this package allowed to exercise the full stack through `default_setup()` rather than constructing components individually.

## Source docs
`14-directory-structure.md`, `02-build-order.md`
