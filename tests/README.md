# `tests/` — repo-root end-to-end security suite

## What this is
One end-to-end test per numbered `SR-x` item (SR-1 through SR-15), each exercising the full, multi-package stack rather than a single package in isolation — the integration-level complement to every package's own `tests/security/` suite.

## Part of
Top-level, alongside `packages/`, `service/`, `tools/`, `docs/`.

## Contains
- `conftest.py` — a full-stack fixture (Recipe A via `default_setup()`, or an equivalent full wiring)
- `security/` — one `test_sr_<NN>_end_to_end_*.py` file per SR item, 1 through 15

## Why divided this way
Kept at the repo root, separate from any single package's `tests/`, because several SR items (e.g. SR-1's hybrid downgrade) are meaningfully testable at the package-internal level *and* need a second, full-stack confirmation that nothing in the wiring between packages reintroduces the vulnerability the package-level test already caught in isolation.

## Dependency rules
- Every file here may import from any package — this is the one test location in the repo explicitly allowed to depend on the full stack at once.

## Source docs
`10-security-requirements.md`, `14-directory-structure.md`
