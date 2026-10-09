# `tests/security/` — end-to-end SR-1 through SR-15

## What this is
Fifteen files, one per numbered SR item, each confirming that SR item holds at the full-stack, wired-system level — not just within the one package where it's primarily implemented.

## Part of
`tests/`.

## Contains
- `test_sr_01_end_to_end_*.py` — SR-1
- `test_sr_02_end_to_end_*.py` — SR-2
- `test_sr_03_end_to_end_*.py` — SR-3
- `test_sr_04_end_to_end_*.py` — SR-4
- `test_sr_05_end_to_end_*.py` — SR-5
- `test_sr_06_end_to_end_*.py` — SR-6
- `test_sr_07_end_to_end_*.py` — SR-7
- `test_sr_08_end_to_end_*.py` — SR-8
- `test_sr_09_end_to_end_*.py` — SR-9
- `test_sr_10_end_to_end_*.py` — SR-10
- `test_sr_11_end_to_end_*.py` — SR-11
- `test_sr_12_end_to_end_*.py` — SR-12
- `test_sr_13_end_to_end_*.py` — SR-13
- `test_sr_14_end_to_end_*.py` — SR-14
- `test_sr_15_end_to_end_*.py` — SR-15

## Why divided this way
One file per `SR-x`, named `test_sr_<NN>_end_to_end_<slug>.py`, mirroring `14-directory-structure.md`'s per-package naming convention but at repo-root scope.

## Dependency rules
- Each file exercises whichever packages that SR item's full-stack scenario actually spans — e.g. SR-1's end-to-end test spans `quantx-combiners` and `quantx-session`/`service`; SR-13's spans only `quantx-compliance`.

## Source docs
`10-security-requirements.md`, `14-directory-structure.md`
