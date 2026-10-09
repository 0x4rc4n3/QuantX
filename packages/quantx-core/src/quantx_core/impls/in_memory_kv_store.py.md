# `in_memory_kv_store.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The reference, dev/test-only `KeyValueStore` implementation backing Recipe A (in-memory everything). Everything stateful in a dev deployment ultimately lands here.

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/impls/`
- **Depends on:** `quantx_core.interfaces.key_value_store.KeyValueStore` (Layer 0 interface this implements)
- **Imported by:** `default_setup.py` (Layer 4, Recipe A wiring)

## Docstring contract
- **Layer:** 0
- **Depends on:** `KeyValueStore` (the interface it implements)
- **Implements:** InMemoryKVStore
- **Outside:** Anything not directly part of this one interface's contract.
- **Inside:** The concrete logic satisfying that contract.
- **Security notes:** **SR-3.** In-memory store has a hard `max_entries` cap — never unbounded.

## Required behavior
- Implements `get`/`set`/`delete` from `KeyValueStore` over an internal dict.
- Enforces a **hard `max_entries` cap** (SR-3) — never unbounded growth. New entries beyond the cap are rejected explicitly, not silently dropped or allowed to grow past the configured limit.
- TTL-backed entries expire — enforced via explicit expiry check against the injected `Clock`, since there's no background eviction process in a plain in-memory dict `(inferred: 07-database-design.md states "explicit expiry check (in-memory)" as the mechanism but doesn't specify lazy-on-read vs. a sweep)`.
- Never used as a production recommendation — this is Recipe A / dev / test only (`06-system-architecture.md`).

## Inputs / outputs
- **In:** `get(key)`, `set(key, value, ttl=None)`, `delete(key)`.
- **Out:** stored bytes or `None`; raises when the `max_entries` cap is hit on `set()`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- `InMemoryKVStore` hits its `max_entries` cap → enforced hard cap, explicit rejection of new entries — not unbounded growth (SR-3, `13-error-and-edge-cases.md`).

## Security notes
- **SR-3.** In-memory store has a hard `max_entries` cap — never unbounded.

## Mandatory tests this must pass
- `tests/impls/test_in_memory_kv_store.py`
- `tests/security/test_sr_03_in_memory_max_entries_cap.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything beyond the one interface this file implements — reference/dev implementations stay narrowly scoped.

## Source docs
`07-database-design.md`, `05-non-functional-requirements.md`, `06-system-architecture.md`, `04-functional-requirements.md`
