# `quantx-combiners` — `tests/`

## What this is
The test suite for Layer 2 — the highest-stakes package. Mirrors `signature/`/`kem/` folder-for-folder, plus the security suite covering SR-1, SR-7, and mandatory wire-parser fuzzing.

## Part of
`quantx-combiners`, Layer 2.

## Contains
- `conftest.py` — shared fixtures (wired-up adapter pairs for both signature and KEM)
- `signature/` — combiner and wire-format tests for the signature side
- `kem/` — combiner and wire-format tests for the KEM side
- `security/` — SR-1, SR-7, and the two mandatory fuzz suites

## Why divided this way
Mirrors `src/` per `14-directory-structure.md`'s ground rules.

## Dependency rules
- Each test file depends only on the files under test in its matching `src/` subfolder, plus shared fixtures.

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`
