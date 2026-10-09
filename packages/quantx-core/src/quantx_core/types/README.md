# `types/` — Layer-0 value types

## What this is
Small, immutable value types shared across every layer — `Mode`, `AlgorithmId`, `TTL`. None of these hold behavior beyond what a frozen value type needs.

## Part of
`quantx-core`, Layer 0.

## Contains
- `mode.py` — `Mode` enum (`HYBRID` / `PQC_ONLY` / `CLASSICAL_ONLY`)
- `algorithm_id.py` — `AlgorithmId`, one member per Layer-1 adapter
- `ttl.py` — `TTL`, the duration type used wherever `KeyValueStore.set()` takes an expiry

## Why divided this way
One value type per file per `14-directory-structure.md`'s atomicity rule — each type is independently imported by different layers, and each is small enough that bundling them would only cost importers unrelated typing surface.

## Dependency rules
- Depends on nothing else in QuantX.
- Imported freely by every layer above — these are the shared vocabulary, not layer-scoped internals.

## Source docs
`04-functional-requirements.md`, `00-index.md`, `14-directory-structure.md`
