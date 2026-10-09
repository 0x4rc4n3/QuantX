# `algorithm_id.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
A value type identifying one concrete algorithm (e.g. `ED25519`, `ML_DSA_65`) — the unit `AlgorithmRegistry` roles and Layer-1 adapters are keyed and reported by, so a role's pairing is always expressed as `AlgorithmId` values, never bare strings.

## Part of
- **Depends on:** nothing internal to QuantX (foundational value type).
- **Imported by:** Every Layer-1 adapter (each reports its own `AlgorithmId`); `algorithm_registry.py`, `registry_role.py` (Layer 3) — a role's pairing is expressed as a pair of `AlgorithmId` values plus a `required_mode`

## Shape
- `AlgorithmId` — a `str`-backed `Enum` (or equivalent frozen value type) with one member per Layer-1 adapter shipped under FR-1.2 (`SLH_DSA` is reserved: it has no adapter until pyca ships SLH-DSA, D-006, and the registry must fail closed on any `AlgorithmId` with no registered adapter): `ED25519`, `ECDSA_P256`, `ML_DSA_65`, `ML_DSA_87`, `SLH_DSA`, `X25519`, `ML_KEM_768`, `ML_KEM_1024` `(inferred exact member names — the docs establish the eight algorithms in FR-1.2 but not this file's literal spelling)`.
- Immutable — one instance per algorithm, referenced by identity/equality, never mutated.

## Non-negotiable principles that apply
- **P2.** One algorithm per adapter file, forever.
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`04-functional-requirements.md`, `04-functional-requirements.md`
