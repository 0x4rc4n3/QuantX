# `test_in_memory_kv_store.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `InMemoryKVStore` correctly implements `KeyValueStore`'s get/set/delete contract and its own hard `max_entries` cap.

## Part of / dependency graph
- **Package:** `quantx-core`, `packages/quantx-core/tests/impls`
- **Depends on:** ``in_memory_kv_store.py`` (the file under test)
- **Imported by:** Nothing — test files are leaves in the dependency graph.

## Docstring contract
- **Layer:** 0
- **Depends on:** `in_memory_kv_store.py`
- **Implements:** pytest test functions, not a production interface.
- **Outside:** Testing anything other than the one file/behavior named in this spec's title.
- **Inside:** The scenarios listed under Required behavior below.
- **Security notes:** See Security notes section below.

## Required behavior
- Round-trips `set` → `get` for arbitrary keys/values.
- `delete` removes a key such that a subsequent `get` returns `None`.
- TTL-backed entries expire per the injected fake `Clock`.
- Confirms the general shape of the `max_entries` cap exists (the specific rejection behavior at the cap is `test_sr_03_in_memory_max_entries_cap.py`'s job, not duplicated here).

## Inputs / outputs
- **In:** fixtures from `conftest.py` plus any test-local fixtures.
- **Out:** pass/fail per `pytest` assertion; no production return value.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `InMemoryKVStore`'s non-security behavior.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Testing any file other than the one named in this spec's title.

## Source docs
`04-functional-requirements.md`, `06-system-architecture.md`
