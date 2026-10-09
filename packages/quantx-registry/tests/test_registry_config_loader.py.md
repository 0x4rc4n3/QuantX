# `test_registry_config_loader.py`

**Package:** `quantx-registry` · **Layer:** 3 — Registry · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `registry_config_loader.py` parses a valid YAML config into `RegistryRole` values using `yaml.safe_load`, and fails fast on a role referencing an unavailable algorithm.

## Part of / dependency graph
- **Package:** `quantx-registry`, `tests/`
- **Depends on:** `registry_config_loader.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 3
- **Depends on:** registry_config_loader.py
- **Implements:** pytest test functions.
- **Outside:** Anything not directly under test here.
- **Inside:** The scenarios in Required behavior.
- **Security notes:** See Security notes below.

## Required behavior
- Loads `algorithm_registry.example.yaml` into a list of `RegistryRole` values.
- A role referencing an unregistered algorithm fails at load time.
- Confirms `yaml.safe_load` is used (no arbitrary object deserialization).

## Inputs / outputs
- **In:** fixtures from `conftest.py`.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `registry_config_loader.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything outside `registry_config_loader.py`.

## Source docs
`06-system-architecture.md`, `13-error-and-edge-cases.md`
