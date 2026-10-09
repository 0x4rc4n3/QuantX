# `ml_kem_768_adapter.py`

**Package:** `quantx-crypto-adapters` · **Layer:** 1 — Algorithm adapters · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Wraps `cryptography` (pyca)'s ML-KEM-768 (FIPS 203, `cryptography.hazmat.primitives.asymmetric.mlkem`) key encapsulation mechanism behind the `KEMProvider` contract — the PQC half of the default hybrid KEM pairing, and the group referenced in the sidecar's required hybrid TLS 1.3 group (X25519MLKEM768, `08-api-specification.md`).

## Part of / dependency graph
- **Package:** `quantx-crypto-adapters`, `src/quantx_crypto_adapters/pqc/`
- **Depends on:** `quantx_core.interfaces.kem_provider.KEMProvider` (Layer 0 interface this implements)
- **Imported by:** `algorithm_registry.py` (Layer 3) — the only place above Layer 1 allowed to import this directly (FR-3.1)
- **Size constraint:** ~30-60 lines target (FR-1.3); if it grows past that, the excess belongs in a different layer, not here.

## Docstring contract
- **Layer:** 1
- **Depends on:** `KEMProvider` (Layer 0)
- **Implements:** `KEMProvider` for ML-KEM-768
- **Outside:** Any branching on algorithm family — this file handles exactly one algorithm and nothing else (FR-1.1, P2).
- **Inside:** ML-KEM-768 key generation, and the encapsulate/decapsulate operations, wrapping `cryptography` (pyca) `MLKEM768PrivateKey`/`MLKEM768PublicKey` — never a hand-rolled primitive (D1).
- **Security notes:** No `SR-x` item is specific to this adapter beyond the FR-0.1-equivalent fail-closed requirement. The PQC backend statement (D-006, `10-security-requirements.md`) applies (`cryptography`-backed).

## Required behavior
- Implements `encapsulate(public_key) -> (ciphertext, shared_secret)` and `decapsulate(ciphertext, private_key) -> shared_secret` for ML-KEM-768 only (FR-1.1).
- Wraps `cryptography` (pyca) `>=48,<51` — never a hand-rolled implementation (D1).
- `decapsulate()` fails closed on malformed input — never raises (FR-0.1-equivalent for the KEM side).
- Ciphertext is exactly 1,088 B and the public key 1,184 B (FIPS 203; matches the ~1.1KB wire-size budget figure in `05-non-functional-requirements.md`). Tests assert the exact sizes.
- Backend mapping: `encapsulate` → `MLKEM768PublicKey.from_public_bytes(public_key).encapsulate()`; `decapsulate` → `MLKEM768PrivateKey.from_seed_bytes(private_key).decapsulate(ciphertext)`. pyca returns `(shared_secret, ciphertext)`, the reverse of the Layer-0 `(ciphertext, shared_secret)`, so the adapter reorders (a test asserts it).
- Key bytes (D-006): the private key is pyca's seed form (64 B, `private_bytes_raw()` / `from_seed_bytes()`); pyca never exports an expanded secret key, so a wallet stores the seed. Public key is 1,184 B, ciphertext 1,088 B, shared secret 32 B. Expanded secret keys from other libraries cannot be imported.
- Implicit rejection (FIPS 203): a well-formed but tampered or wrong-key ciphertext does not raise; `decapsulate` returns a different pseudorandom secret. Only wrong-length input raises `ValueError`, which the adapter turns into its fail-closed result. Tamper detection therefore comes from the KEM combiner's HKDF ciphertext/public-key binding (SR-7) and downstream authentication, not from this adapter, and the docstring must not claim otherwise (P6).
- Backend support is probed at construction; `UnsupportedAlgorithm` from the backend is raised as an explicit typed error, never converted into a fail-closed "bad ciphertext" result.

## Inputs / outputs
- **In:** `encapsulate`: a public key (`bytes`). `decapsulate`: ciphertext + private key (`bytes`, `bytes`).
- **Out:** `encapsulate`: `(ciphertext ~1.1KB, shared_secret)`. `decapsulate`: `shared_secret`, or a fail-closed rejection on malformed input.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Signature/KEM bytes are malformed or truncated → `verify()`/`decapsulate()` catches the parse/crypto-library failure internally and returns `False` (or fails closed) — never raises (FR-0.1, `13-error-and-edge-cases.md`).

## Security notes
- No `SR-x` item is specific to this adapter beyond the FR-0.1-equivalent fail-closed requirement. The PQC backend statement (D-006, `10-security-requirements.md`) applies (`cryptography`-backed).
- Any material referencing this adapter states the backing library and its maturity per the PQC backend statement (D-006, `10-security-requirements.md`) — this isn't a one-time disclaimer, it's checked per-artifact.

## Mandatory tests this must pass
- `tests/pqc/test_ml_kem_768_adapter.py`
- `tests/security/test_verify_fails_closed_on_malformed_input.py` (parametrized across every adapter, this one included)

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P2.** One algorithm per adapter file, forever.

## Explicitly out of scope for this file
- Any other algorithm — one algorithm per adapter file, forever (P2).
- Combining this with another algorithm into a hybrid result — that's `SignatureCombiner`/`KEMCombiner`'s job (Layer 2), constructor-wired, not built here.
- Deciding when this algorithm is used — that's `AlgorithmRegistry`'s job (Layer 3).

## Source docs
`08-api-specification.md`, `05-non-functional-requirements.md`, `04-functional-requirements.md`, `06-system-architecture.md`, `02-build-order.md`
