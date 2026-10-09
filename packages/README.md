# `packages/` — the ten layered, independently-publishable libraries

## What this is
The ten packages implementing QuantX's Layer 0-10 architecture, each independently publishable, each depending only on the layers below it (`01-product-requirements.md`, `06-system-architecture.md`).

## Part of
Top-level, alongside `service/`, `tools/`, `docs/`.

## Contains
- `quantx-core` — Layer 0: foundational interfaces, types, exceptions, reference impls
- `quantx-crypto-adapters` — Layer 1: one file per algorithm, classical + PQC
- `quantx-combiners` — Layer 2: `SignatureCombiner`, `KEMCombiner` (`GATE_REVIEW_REQUIRED`)
- `quantx-registry` — Layer 3: `AlgorithmRegistry` (`GATE_REVIEW_REQUIRED`)
- `quantx-session` — Layer 4: challenge/session orchestration, the Recipe-A demo
- `quantx-authenticator` — Layer 5: TOTP/HOTP/push second factors
- `quantx-wallet` — Layers 6-7: key custody (`GATE_REVIEW_REQUIRED` backends) and recovery
- `quantx-threshold` — Layer 8: m-of-n policies (`GATE_REVIEW_REQUIRED`)
- `quantx-zkp` — Layer 9: Merkle membership proofs (`GATE_REVIEW_REQUIRED`)
- `quantx-compliance` — Layer 10: crypto BOM, standards catalog, scanners

## Why divided this way
Each layer is independently publishable (`01-product-requirements.md`'s "shipped as independently-publishable Python packages") and the dependency direction is strictly downward (a package depends only on lower-numbered layers), per `06-system-architecture.md`'s layer table.

## Dependency rules
- Package N depends only on packages implementing layers below N — never sideways, never up.
- Only `algorithm_registry.py` (Layer 3) is permitted to import every Layer-1 adapter directly (FR-3.1, FR-X.2) — every other cross-layer dependency goes through a Layer-0 interface (P1).

## Source docs
`01-product-requirements.md`, `06-system-architecture.md`, `14-directory-structure.md`
