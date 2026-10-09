# `classical/` — classical algorithm adapters

## What this is
The three classical (pre-PQC) algorithm adapters: Ed25519 and ECDSA-P256 for signatures, X25519 for key exchange. Each wraps `cryptography` (pyca) behind a Layer-0 interface.

## Part of
`quantx-crypto-adapters`, Layer 1.

## Contains
- `ed25519_adapter.py` — `Signer`/`Verifier` for Ed25519
- `ecdsa_p256_adapter.py` — `Signer`/`Verifier` for ECDSA-P256
- `x25519_adapter.py` — `KEMProvider` for X25519

## Why divided this way
One algorithm per file, forever (P2, FR-1.1) — split from `pqc/` so the PQC-specific backend probe, key-format notes and maturity statement stay scoped to exactly the files that need them.

## Dependency rules
- Each adapter depends only on its one Layer-0 interface (`Signer`, `Verifier`, or `KEMProvider`).
- Uses `cryptography` (pyca) exclusively — mature, audited primitives per `06-system-architecture.md`'s tech-stack table. The PQC adapters use the same package's newer ML-KEM/ML-DSA modules (see `../pqc/README.md`).
- No adapter here imports another adapter, classical or PQC (P1, FR-X.2).

## Independently publishable?
N/A — a subfolder within the `quantx-crypto-adapters` package, not itself independently publishable.

## Source docs
`04-functional-requirements.md`, `06-system-architecture.md`, `14-directory-structure.md`
