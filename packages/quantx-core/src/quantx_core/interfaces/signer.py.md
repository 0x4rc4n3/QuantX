# `signer.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Defines the `Signer` `Protocol` — one of the eight foundational Layer-0 interfaces every algorithm-agile component above it is built against, never against a concrete implementation directly (P1).

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/interfaces/`
- **Depends on:** nothing — this is a foundational `Protocol`, Layer 0's own contract.
- **Imported by:** `ed25519_adapter.py`, `ecdsa_p256_adapter.py`, `ml_dsa_65_adapter.py`, `ml_dsa_87_adapter.py`, `slh_dsa_adapter.py` (Layer 1, each implements it); `signature_combiner.py` (Layer 2, type-hints its constructor against this interface, per P1)

## Docstring contract
- **Layer:** 0
- **Depends on:** Nothing internal.
- **Implements:** `sign(message: bytes) -> bytes`
- **Outside:** Choice of which concrete algorithm is used — that's `AlgorithmRegistry` (Layer 3) and constructor wiring, never this file.
- **Inside:** The method signature every classical/PQC signature adapter (Layer 1) must satisfy.
- **Security notes:** Carries no security guarantee itself — a `Protocol` has no runtime behavior to secure. The guarantee is only as strong as whichever concrete adapter is wired in.

## Required behavior
- `Signer` is a `typing.Protocol` (structural typing) — any object with the right method shape satisfies it; no component is required to subclass it explicitly.
- No default/concrete logic lives here — this file defines a contract only.

## Inputs / outputs
- **In/Out:** defined per-method by the `Protocol`; see `Docstring contract` above.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- Carries no security guarantee itself — a `Protocol` has no runtime behavior to secure. The guarantee is only as strong as whichever concrete adapter is wired in.

## Mandatory tests this must pass
- No dedicated test file — a `Protocol` has no behavior of its own to test; conformance is exercised indirectly by every concrete implementation's own test suite.

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any concrete implementation — those live in `impls/`.

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`
