# `canonicalizer.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Defines the `Canonicalizer` `Protocol` — one of the eight foundational Layer-0 interfaces every algorithm-agile component above it is built against, never against a concrete implementation directly (P1).

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/interfaces/`
- **Depends on:** nothing — this is a foundational `Protocol`, Layer 0's own contract.
- **Imported by:** `jcs_canonicalizer.py` (Layer 0 impl, the only concrete implementation that should exist); `challenge_issuer.py`, `session_orchestrator.py` (Layer 4), `registry_config_signature.py` (Layer 3) — anything that canonicalizes data before signing

## Docstring contract
- **Layer:** 0
- **Depends on:** Nothing internal.
- **Implements:** `canonicalize(data: Mapping) -> bytes`
- **Outside:** Deciding *what* gets canonicalized and signed — that's each caller's job.
- **Inside:** The single method every canonicalization implementation must provide.
- **Security notes:** FR-0.4 / SR-8 — this Protocol exists so that exactly one canonicalization path (`jcs_canonicalizer.py`) is reachable system-wide for anything that gets signed. The interface itself doesn't enforce single-path use — that's `tools/lint/check_single_canonicalization_path.py`'s job — but naming it here is what gives that lint check something unambiguous to check against.

## Required behavior
- `Canonicalizer` is a `typing.Protocol` defining `canonicalize(data) -> bytes`.
- FR-0.4: `Canonicalizer.canonicalize()` is the only path by which structured data becomes bytes before signing, system-wide — this is a system-wide constraint this interface exists to make checkable, not a behavior this file itself implements.

## Inputs / outputs
- **In/Out:** defined per-method by the `Protocol`; see `Docstring contract` above.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **SR-8.** Exactly one canonicalization path is used for anything signed, system-wide — enforced by having exactly one concrete implementation (`jcs_canonicalizer.py`) and a CI lint check (`tools/lint/check_single_canonicalization_path.py`) that fails if any other file serializes data for signing.

## Mandatory tests this must pass
- No dedicated test file — a `Protocol` has no behavior of its own to test; conformance is exercised indirectly by every concrete implementation's own test suite.

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any concrete implementation — those live in `impls/`.

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`
