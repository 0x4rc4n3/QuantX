# `pqc/` — post-quantum algorithm adapters

## What this is
The PQC algorithm adapters: ML-DSA-65 and ML-DSA-87 for signatures; ML-KEM-768 and ML-KEM-1024 for key encapsulation. Each wraps `cryptography` (pyca) behind a Layer-0 interface. SLH-DSA is specified but blocked until pyca ships it (D-006).

## Part of
`quantx-crypto-adapters`, Layer 1.

## Contains
- `ml_dsa_65_adapter.py` — `Signer`/`Verifier` for ML-DSA-65 (default hybrid PQC signature half)
- `ml_dsa_87_adapter.py` — `Signer`/`Verifier` for ML-DSA-87 (higher security level)
- `slh_dsa_adapter.py` — **spec only, blocked on pyca (D-006); not created yet.** `Signer`/`Verifier` for SLH-DSA (hash-based, structurally distinct from ML-DSA)
- `ml_kem_768_adapter.py` — `KEMProvider` for ML-KEM-768 (default hybrid PQC KEM half)
- `ml_kem_1024_adapter.py` — `KEMProvider` for ML-KEM-1024 (higher security level)

## Why divided this way
One algorithm per file, forever (P2, FR-1.1) — split from `classical/` so the PQC-specific backend probe, key-format notes (seed-only private keys) and maturity statement stay scoped to exactly the files that need them.

## Dependency rules
- Each adapter depends only on its one Layer-0 interface.
- Uses `cryptography` (pyca) `>=48,<51` exclusively. Its ML-KEM/ML-DSA support is recent and depends on the backend the wheel or build uses (OpenSSL >=3.5, AWS-LC, BoringSSL); mitigated by mandatory hybrid mode (D2). Backend support is probed at construction and fails loudly. Every artifact referencing any file in this folder must carry the PQC backend statement (D-006, `10-security-requirements.md`).
- No adapter here imports another adapter, classical or PQC (P1, FR-X.2).

## Independently publishable?
N/A — a subfolder within the `quantx-crypto-adapters` package.

## Source docs
`04-functional-requirements.md`, `06-system-architecture.md`, `10-security-requirements.md`
