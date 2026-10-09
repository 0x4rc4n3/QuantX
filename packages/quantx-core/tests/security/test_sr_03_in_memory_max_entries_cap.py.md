# `test_sr_03_in_memory_max_entries_cap.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms `InMemoryKVStore` enforces a hard `max_entries` cap and explicitly rejects new entries beyond it, rather than growing unbounded.

## Part of / dependency graph
- **Package:** `quantx-core`, `packages/quantx-core/tests/security`
- **Depends on:** ``in_memory_kv_store.py`` (the file under test)
- **Imported by:** Nothing — test files are leaves in the dependency graph.

## Docstring contract
- **Layer:** 0
- **Depends on:** `in_memory_kv_store.py`
- **Implements:** The mandatory automated security test for SR-3 (`10-security-requirements.md`).
- **Outside:** Anything not directly required to prove or disprove this one SR item.
- **Inside:** The specific attack/failure scenario named in Required behavior below.
- **Security notes:** This file **is** the enforcement check for SR-3.

## Required behavior
- Fill the store to its configured `max_entries` limit.
- Attempt one more `set()` → must be explicitly rejected (raised error or documented rejection return), never silently accepted.
- Confirm no unbounded growth occurs under sustained `set()` calls past the cap.

## Inputs / outputs
- **In:** fixtures from `conftest.py`, crafted adversarial input specific to this SR item.
- **Out:** pass/fail; a failing run here is a release blocker per `10-security-requirements.md`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-3.** This file is the named, dedicated enforcement test for SR-3 — per `14-directory-structure.md`'s naming convention, its filename alone answers "where's the test for SR-3".

## Mandatory tests this must pass
- This file *is* the mandatory test for SR-3 — nothing else satisfies it.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Testing any SR item other than the one named in this file's title.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`
