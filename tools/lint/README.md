# `lint/` — custom CI architectural lint checks

## What this is
Three custom static checks enforcing architectural rules a type checker alone can't catch: docstring-contract completeness, the sibling-import ban, and the single-canonicalization-path rule.

## Part of
`tools/`.

## Contains
- `check_docstring_contract.py` — every module docstring has all required fields, in order (FR-X.1)
- `check_no_sibling_imports.py` — no component above Layer 1 imports a sibling concrete class, except `AlgorithmRegistry` (FR-X.2)
- `check_single_canonicalization_path.py` — nothing outside `jcs_canonicalizer.py` serializes data for signing (SR-8)

## Why divided this way
Three independent static checks, each enforcing one architectural rule, kept separate so a CI failure in one names exactly which rule broke.

## Dependency rules
- Each script scans the `packages/`/`service/` source tree read-only — none modifies source, and none depends on another lint script.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`
