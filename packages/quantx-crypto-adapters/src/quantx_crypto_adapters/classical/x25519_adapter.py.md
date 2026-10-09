# `x25519_adapter.py`

**Package:** `quantx-crypto-adapters` · **Layer:** 1 — Algorithm adapters · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Wraps the `cryptography` package's X25519 key exchange behind the `KEMProvider` contract — the classical half of the default hybrid KEM pairing.

## Part of / dependency graph
- **Package:** `quantx-crypto-adapters`, `src/quantx_crypto_adapters/classical/`
- **Depends on:** `quantx_core.interfaces.kem_provider.KEMProvider` (Layer 0 interface this implements)
- **Imported by:** `algorithm_registry.py` (Layer 3) — the only place above Layer 1 allowed to import this directly (FR-3.1)
- **Size constraint:** ~30-60 lines target (FR-1.3); if it grows past that, the excess belongs in a different layer, not here.

## Docstring contract
- **Layer:** 1
- **Depends on:** `KEMProvider` (Layer 0)
- **Implements:** `KEMProvider` for X25519
- **Outside:** Any branching on algorithm family — this file handles exactly one algorithm and nothing else (FR-1.1, P2).
- **Inside:** X25519 key generation, and the encapsulate/decapsulate operations, wrapping `cryptography` — never a hand-rolled primitive (D1).
- **Security notes:** No `SR-x` item is specific to this adapter beyond the general FR-0.1-equivalent fail-closed requirement for `decapsulate()`. The HKDF binding that makes ciphertext/public-key substitution detectable (SR-7) lives one layer up, in `kem_hkdf_binding.py`.

## Required behavior
- Implements `encapsulate(public_key) -> (ciphertext, shared_secret)` and `decapsulate(ciphertext, private_key) -> shared_secret` for X25519 only (FR-1.1). Mapping (D-015): `encapsulate` generates a fresh ephemeral key pair per call, the ciphertext is the 32-byte ephemeral public key, the shared secret is the raw Diffie-Hellman output, and an all-zero output is rejected. The combiner binds both sides in the HKDF input (V2 §7).
- Uses `cryptography` (pyca), never a hand-rolled implementation (D1).
- `decapsulate()` fails closed on malformed input — catches internally, never raises (FR-0.1 applied to the KEM side, per `02-build-order.md`'s Layer-1 definition of done).

## Inputs / outputs
- **In:** `encapsulate`: a public key (`bytes`). `decapsulate`: ciphertext + private key (`bytes`, `bytes`).
- **Out:** `encapsulate`: `(ciphertext, shared_secret)`. `decapsulate`: `shared_secret`, or a fail-closed rejection on malformed input.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Signature/KEM bytes are malformed or truncated → `verify()`/`decapsulate()` catches the parse/crypto-library failure internally and returns `False` (or fails closed) — never raises (FR-0.1, `13-error-and-edge-cases.md`).

## Security notes
- No `SR-x` item is specific to this adapter beyond the general FR-0.1-equivalent fail-closed requirement for `decapsulate()`. The HKDF binding that makes ciphertext/public-key substitution detectable (SR-7) lives one layer up, in `kem_hkdf_binding.py`.

## Mandatory tests this must pass
- `tests/classical/test_x25519_adapter.py`
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
