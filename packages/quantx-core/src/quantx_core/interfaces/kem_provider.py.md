# `kem_provider.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Defines the `KEMProvider` `Protocol` — one of the eight foundational Layer-0 interfaces every algorithm-agile component above it is built against, never against a concrete implementation directly (P1).

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/interfaces/`
- **Depends on:** nothing — this is a foundational `Protocol`, Layer 0's own contract.
- **Imported by:** `x25519_adapter.py`, `ml_kem_768_adapter.py`, `ml_kem_1024_adapter.py` (Layer 1, each implements it); `kem_combiner.py` (Layer 2, type-hints its constructor against this interface, per P1)

## Docstring contract
- **Layer:** 0
- **Depends on:** Nothing internal.
- **Implements:** `encapsulate(public_key: bytes) -> tuple[bytes, bytes]` (ciphertext, shared_secret); `decapsulate(ciphertext: bytes, private_key: bytes) -> bytes`
- **Outside:** HKDF binding of ciphertext/public key (`kem_hkdf_binding.py`, SR-7) — that's Layer 2's job, not this interface's.
- **Inside:** The encapsulate/decapsulate method shape every KEM adapter must satisfy.
- **Security notes:** No guarantee of its own; SR-7's ciphertext/public-key binding is enforced by `KEMCombiner`, one layer up, not by this Protocol.

## Required behavior
- `KEMProvider` is a `typing.Protocol` (structural typing) — any object with the right method shape satisfies it; no component is required to subclass it explicitly.
- No default/concrete logic lives here — this file defines a contract only.

## Inputs / outputs
- **In/Out:** defined per-method by the `Protocol`; see `Docstring contract` above.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No guarantee of its own; SR-7's ciphertext/public-key binding is enforced by `KEMCombiner`, one layer up, not by this Protocol.

## Mandatory tests this must pass
- No dedicated test file — a `Protocol` has no behavior of its own to test; conformance is exercised indirectly by every concrete implementation's own test suite.

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any concrete implementation — those live in `impls/`.

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`
