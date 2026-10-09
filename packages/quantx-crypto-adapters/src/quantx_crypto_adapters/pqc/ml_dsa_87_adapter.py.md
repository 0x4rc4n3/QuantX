# `ml_dsa_87_adapter.py`

**Package:** `quantx-crypto-adapters` · **Layer:** 1 — Algorithm adapters · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Wraps `cryptography` (pyca)'s ML-DSA-87 (FIPS 204, `cryptography.hazmat.primitives.asymmetric.mldsa`) signature scheme behind the `Signer`/`Verifier` contract — available alongside ML-DSA-65 for pairings that need the higher parameter set.

## Part of / dependency graph
- **Package:** `quantx-crypto-adapters`, `src/quantx_crypto_adapters/pqc/`
- **Depends on:** `quantx_core.interfaces.signer.Signer` (Layer 0 interface this implements)
- **Imported by:** `algorithm_registry.py` (Layer 3) — the only place above Layer 1 allowed to import this directly (FR-3.1)
- **Size constraint:** ~30-60 lines target (FR-1.3); if it grows past that, the excess belongs in a different layer, not here.

## Docstring contract
- **Layer:** 1
- **Depends on:** `Signer` (Layer 0)
- **Implements:** `Signer` for ML-DSA-87
- **Outside:** Any branching on algorithm family — this file handles exactly one algorithm and nothing else (FR-1.1, P2).
- **Inside:** ML-DSA-87 key generation, and the sign/verify operations, wrapping `cryptography` (pyca) `MLDSA87PrivateKey`/`MLDSA87PublicKey` — never a hand-rolled primitive (D1).
- **Security notes:** No `SR-x` item is specific to this adapter beyond FR-0.1. The PQC backend statement (D-006, `10-security-requirements.md`) applies (`cryptography`-backed).

## Required behavior
- Implements `generate_keypair`, `sign(message) -> bytes`, and satisfies `Verifier.verify(message, signature) -> bool` for ML-DSA-87 only (FR-1.1).
- Wraps `cryptography` (pyca) `>=48,<51` — never a hand-rolled implementation (D1).
- `verify()` catches any internal exception and returns `False` — never raises (FR-0.1).
- Backend mapping: `generate_keypair` → `MLDSA87PrivateKey.generate()`; `sign` → `private_key.sign(message)`; `verify` → `public_key.verify(signature, message)`. pyca's `verify` takes `(signature, data)`, the reverse of the Layer-0 `verify(message, signature)` order, so the adapter reorders (a test asserts swapped arguments do not verify).
- Key bytes (D-006): the private key is pyca's seed form (32 B, `private_bytes_raw()` / `from_seed_bytes()`); pyca never exports an expanded secret key, so a wallet stores the seed. Public key is `public_bytes_raw()` (2,592 B); signature is 4,627 B. Expanded secret keys from other libraries cannot be imported.
- No ML-DSA context string is used (`context=None` on both sides). Using one later changes the signature format and must be specified in the wire format first (domain separation is handled by the D-009 payload prefix, so keep `context=None`).
- `verify()` returns `False` on `cryptography.exceptions.InvalidSignature` and on `ValueError`/`TypeError` from wrong-length or malformed inputs (FR-0.1). It must **not** swallow `UnsupportedAlgorithm`: backend support is probed at construction, and a backend without ML-DSA-87 raises an explicit typed error then. A missing backend must never look like a failed verification.

## Inputs / outputs
- **In:** `sign`: a message (`bytes`). `verify`: message + signature (`bytes`, `bytes`).
- **Out:** `sign`: an ML-DSA-87 signature (larger than ML-DSA-65's). `verify`: `bool`, never raises.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Signature/KEM bytes are malformed or truncated → `verify()`/`decapsulate()` catches the parse/crypto-library failure internally and returns `False` (or fails closed) — never raises (FR-0.1, `13-error-and-edge-cases.md`).

## Security notes
- No `SR-x` item is specific to this adapter beyond FR-0.1. The PQC backend statement (D-006, `10-security-requirements.md`) applies (`cryptography`-backed).
- Any material referencing this adapter states the backing library and its maturity per the PQC backend statement (D-006, `10-security-requirements.md`) — this isn't a one-time disclaimer, it's checked per-artifact.

## Mandatory tests this must pass
- `tests/pqc/test_ml_dsa_87_adapter.py`
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
