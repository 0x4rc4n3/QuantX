# `verifier.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Defines the `Verifier` `Protocol` — one of the eight foundational Layer-0 interfaces every algorithm-agile component above it is built against, never against a concrete implementation directly (P1).

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/interfaces/`
- **Depends on:** nothing — this is a foundational `Protocol`, Layer 0's own contract.
- **Imported by:** `ed25519_adapter.py`, `ecdsa_p256_adapter.py`, `ml_dsa_65_adapter.py`, `ml_dsa_87_adapter.py`, `slh_dsa_adapter.py` (Layer 1, each implements it); `signature_combiner.py` (Layer 2, verifies each component signature through this contract)

## Docstring contract
- **Layer:** 0
- **Depends on:** Nothing internal.
- **Implements:** `verify(message: bytes, signature: bytes) -> bool`
- **Outside:** Deciding *which* algorithm's verifier is in play — that's registry/combiner concern.
- **Inside:** The one required behavioral guarantee: `verify()` never raises (FR-0.1).
- **Security notes:** FR-0.1 — `Verifier.verify()` never raises; any internal exception (malformed signature bytes, wrong key size, etc.) is caught internally by the concrete adapter and converted to a `False` return, so callers never need a try/except around a verify call.

## Required behavior
- `Verifier` is a `typing.Protocol` defining exactly one method: `verify(message, signature) -> bool`.
- FR-0.1 is binding on every concrete implementation of this Protocol, not on this file itself (a Protocol has no body to raise from) — this file's job is to make FR-0.1 impossible to miss by stating it directly in the contract every adapter is written against.

## Inputs / outputs
- **In/Out:** defined per-method by the `Protocol`; see `Docstring contract` above.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **FR-0.1 / (foundational).** Every class implementing this Protocol must catch its own internal exceptions inside `verify()` and return `False` — never propagate. Enforced per-adapter, not here.

## Mandatory tests this must pass
- No dedicated test file — a `Protocol` has no behavior of its own to test; conformance is exercised indirectly by every concrete implementation's own test suite.

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any concrete implementation — those live in `impls/`.

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`
