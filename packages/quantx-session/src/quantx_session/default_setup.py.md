# `default_setup.py`

**Package:** `quantx-session` · **Layer:** 4 — Session · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The Recipe-A wiring helper — `default_setup()` — constructing `Clock`, `KeyValueStore`, `Canonicalizer`, `AlgorithmRegistry`, combiners, and `SessionOrchestrator` with sane in-memory defaults, so an integrator gets a working hybrid-auth demo in three calls: `default_setup() → start() → finish() → validate()` (`01-product-requirements.md`).

## Part of / dependency graph
- **Package:** `quantx-session`, `src/quantx_session`
- **Depends on:** Every Layer 0-4 component this recipe wires: `SystemClock`, `InMemoryKVStore`, `JCSCanonicalizer`, `InMemoryReplayStore`, `InMemoryRateLimiter` (Layer 0); every Layer-1 adapter (indirectly, via `AlgorithmRegistry`); `AlgorithmRegistry` with `allow_unsigned=True` (Layer 3); `ChallengeIssuer`, `SessionOrchestrator` (this package)
- **Imported by:** Integrator code and the demo/example test (`test_default_setup_end_to_end_demo.py`); not imported by any other production component

## Docstring contract
- **Layer:** 4
- **Depends on:** Every Layer 0-4 component Recipe A composes.
- **Implements:** `default_setup() -> (SessionOrchestrator, TotpProvider | None)` or equivalent
- **Outside:** Recipe B/C wiring — those are client-specific compositions, not this file's job.
- **Inside:** Constructing the full in-memory Recipe-A object graph in one call.
- **Security notes:** Uses `allow_unsigned=True` for the registry — appropriate for Recipe A only, never a pattern to copy for Recipe B/C (FR-3.3).

## Required behavior
- Constructs `Clock`, `KeyValueStore`, `Canonicalizer`, `AlgorithmRegistry` (with `allow_unsigned=True`), a combiner pair, and `SessionOrchestrator` — Recipe A: in-memory everything, unsigned registry config, raw keys in memory (`06-system-architecture.md`).
- Returns the wired orchestrator (plus TOTP if Layer 5 is included in the demo path) so an integrator can immediately call `start(subject_id) → finish(signed) → validate(token)` without touching any component's internals (`03-user-stories-and-flows.md`).
- This composition is a convenience wiring helper, not a new architectural concept — swapping any one constructor argument here (e.g. `InMemoryKVStore` → `RedisKVStore`) is exactly Recipe A → Recipe B, requiring zero changes to Layers 1-4 themselves (`01-product-requirements.md`'s core value proposition, made falsifiable).

## Inputs / outputs
- **In:** none (or minimal recipe-selection parameters).
- **Out:** a fully wired `SessionOrchestrator` (and, once Layer 5 lands, `TotpProvider`).

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **FR-3.3 (dev-only path).** `allow_unsigned=True` is correct here specifically because this is Recipe A — this file must never be the template copied for a Recipe B/C wiring.

## Mandatory tests this must pass
- `tests/test_default_setup_end_to_end_demo.py` — the `default_setup → start → finish → validate` demo, in full

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.

## Explicitly out of scope for this file
- Recipe B (networked backend, signed config, real key custody) and Recipe C (PQC-only) wiring — those are client-specific compositions built per engagement, not shipped as a second helper function in this file.

## Source docs
`06-system-architecture.md`, `01-product-requirements.md`, `03-user-stories-and-flows.md`, `02-build-order.md`, `04-functional-requirements.md`
