# `ecdsa_p256_adapter.py`

**Package:** `quantx-crypto-adapters` · **Layer:** 1 — Algorithm adapters · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Wraps the `cryptography` package's ECDSA-P256 implementation behind the `Signer`/`Verifier` contract — a classical adapter available for pairings that need it, alongside Ed25519.

## Part of / dependency graph
- **Package:** `quantx-crypto-adapters`, `src/quantx_crypto_adapters/classical/`
- **Depends on:** `quantx_core.interfaces.signer.Signer` (Layer 0 interface this implements)
- **Imported by:** `algorithm_registry.py` (Layer 3) — the only place above Layer 1 allowed to import this directly (FR-3.1)
- **Size constraint:** ~30-60 lines target (FR-1.3); if it grows past that, the excess belongs in a different layer, not here.

## Docstring contract
- **Layer:** 1
- **Depends on:** `Signer` (Layer 0)
- **Implements:** `Signer` for ECDSA-P256
- **Outside:** Any branching on algorithm family — this file handles exactly one algorithm and nothing else (FR-1.1, P2).
- **Inside:** ECDSA-P256 key generation, and the sign/verify operations, wrapping `cryptography` — never a hand-rolled primitive (D1).
- **Security notes:** No `SR-x` item is specific to this adapter beyond the general FR-0.1 fail-closed requirement.

## Required behavior
- Implements `generate_keypair`, `sign(message) -> bytes`, and satisfies `Verifier.verify(message, signature) -> bool` for ECDSA-P256 only (FR-1.1).
- Uses `cryptography` (pyca), never a hand-rolled implementation (D1).
- `verify()` catches any internal exception and returns `False` — never raises (FR-0.1).
- Full round-trip `generate_keypair → sign → verify` must succeed for a genuine keypair/message.

## Inputs / outputs
- **In:** `sign`: a message (`bytes`). `verify`: message + signature (`bytes`, `bytes`).
- **Out:** `sign`: a DER-encoded ECDSA signature. `verify`: `bool`, never raises.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Signature/KEM bytes are malformed or truncated → `verify()`/`decapsulate()` catches the parse/crypto-library failure internally and returns `False` (or fails closed) — never raises (FR-0.1, `13-error-and-edge-cases.md`).

## Security notes
- No `SR-x` item is specific to this adapter beyond the general FR-0.1 fail-closed requirement.

## Mandatory tests this must pass
- `tests/classical/test_ecdsa_p256_adapter.py`
- `tests/security/test_verify_fails_closed_on_malformed_input.py` (parametrized across every adapter, this one included)

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P2.** One algorithm per adapter file, forever.

## Explicitly out of scope for this file
- Any other algorithm — one algorithm per adapter file, forever (P2).
- Combining this with another algorithm into a hybrid result — that's `SignatureCombiner`/`KEMCombiner`'s job (Layer 2), constructor-wired, not built here.
- Deciding when this algorithm is used — that's `AlgorithmRegistry`'s job (Layer 3).

## Source docs
`04-functional-requirements.md`, `06-system-architecture.md`, `02-build-order.md`
