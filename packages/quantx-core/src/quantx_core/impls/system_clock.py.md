# `system_clock.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The production `Clock` implementation — the one place in the entire codebase permitted to read wall-clock time.

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/impls/`
- **Depends on:** `quantx_core.interfaces.clock.Clock` (Layer 0 interface this implements)
- **Imported by:** `default_setup.py` (Layer 4, Recipe A wiring) and, transitively, every timestamp-consuming component wired through it

## Docstring contract
- **Layer:** 0
- **Depends on:** `Clock` (the interface it implements)
- **Implements:** SystemClock
- **Outside:** Anything not directly part of this one interface's contract.
- **Inside:** The concrete logic satisfying that contract.
- **Security notes:** **SR-14.** Timestamps come only from an injected `Clock`, never `or`-defaulted against wall-clock reads.

## Required behavior
- Implements `now()` by reading the actual system clock — this is deliberately the *only* file in the codebase that does so (SR-14).
- No `or`-defaulting, no fallback value — a caller either gets a real timestamp from this class or the constructor wiring is wrong, which is a config error to catch at wiring time, not runtime.

## Inputs / outputs
- **In:** none.
- **Out:** the current timestamp.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Every timestamp-consuming component takes this (or a test double) via constructor injection — never reads time directly itself (SR-14).

## Security notes
- **SR-14.** Timestamps come only from an injected `Clock`, never `or`-defaulted against wall-clock reads.

## Mandatory tests this must pass
- `tests/impls/test_system_clock.py`
- `tests/security/test_sr_14_clock_never_defaults.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything beyond the one interface this file implements — reference/dev implementations stay narrowly scoped.

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`
