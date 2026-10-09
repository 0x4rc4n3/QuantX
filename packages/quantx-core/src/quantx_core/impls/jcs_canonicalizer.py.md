# `jcs_canonicalizer.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The one and only canonicalization implementation in the system — RFC 8785 (JCS) — used everywhere structured data must become bytes before signing.

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/impls/`
- **Depends on:** `quantx_core.interfaces.canonicalizer.Canonicalizer` (Layer 0 interface this implements)
- **Imported by:** `challenge_issuer.py`, `session_orchestrator.py` (Layer 4); `registry_config_signature.py` (Layer 3)

## Docstring contract
- **Layer:** 0
- **Depends on:** `Canonicalizer` (the interface it implements)
- **Implements:** JCSCanonicalizer
- **Outside:** Anything not directly part of this one interface's contract.
- **Inside:** The concrete logic satisfying that contract.
- **Wire format:** RFC 8785 (JCS) — deterministic key ordering, no insignificant whitespace.
- **Security notes:** **SR-8 / FR-0.4.** Exactly one canonicalization path is used for anything signed, system-wide.

## Required behavior
- Implements `canonicalize(data) -> bytes` per RFC 8785 JavaScript Object Notation Canonicalization Scheme.
- This is the **only** concrete `Canonicalizer` implementation that should exist in the codebase (FR-0.4, SR-8) — `tools/lint/check_single_canonicalization_path.py` fails CI if any other file serializes data for signing outside this class.
- Reference implementation, no external dependency needed (`06-system-architecture.md`'s tech stack table).

## Inputs / outputs
- **In:** a `Mapping` (structured data to be signed).
- **Out:** canonical bytes, deterministic for a given logical input regardless of key order.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-8 / FR-0.4.** Exactly one canonicalization path is used for anything signed, system-wide.

## Mandatory tests this must pass
- `tests/impls/test_jcs_canonicalizer.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything beyond the one interface this file implements — reference/dev implementations stay narrowly scoped.

## Source docs
`06-system-architecture.md`, `06-system-architecture.md`, `04-functional-requirements.md`
