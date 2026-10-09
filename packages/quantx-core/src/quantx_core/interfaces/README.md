# `interfaces/` — Layer-0 foundational Protocols

## What this is
The eight `Protocol`-typed contracts every other layer in QuantX is built against. Nothing in this folder has behavior — each file defines a method shape, not an implementation.

## Part of
`quantx-core`, Layer 0. The lowest layer in the dependency graph — nothing here depends on anything else in QuantX.

## Contains
- `signer.py` — `Signer` Protocol (Layer-1 signature adapters implement this)
- `verifier.py` — `Verifier` Protocol (FR-0.1: `verify()` never raises)
- `kem_provider.py` — `KEMProvider` Protocol (Layer-1 KEM adapters implement this)
- `canonicalizer.py` — `Canonicalizer` Protocol (FR-0.4 / SR-8: the one path to bytes-before-signing)
- `clock.py` — `Clock` Protocol (FR-0.3 / SR-14: the one path to the current time)
- `key_value_store.py` — `KeyValueStore` Protocol (FR-0.2: the one path to persistence)
- `replay_store.py` — `ReplayStore` Protocol (FR-4.2 / SR-11: consume-once semantics)
- `rate_limiter.py` — `RateLimiter` Protocol (FR-4.4: per-identity and global gating)

## Why divided this way
One `Protocol` per file, per `14-directory-structure.md`'s atomic-split rule — each interface is independently referenced by different layers above, and bundling them into one `interfaces.py` would force any importer to pull in every interface's typing surface just to use one.

## Dependency rules
- Nothing in this folder imports anything else in QuantX (P1 — this is the foundation constructors are inverted *against*).
- Every concrete implementation elsewhere in the codebase (Layer 1 adapters, `impls/`, and components in every higher layer) type-hints its constructor parameters against these Protocols, never against a concrete sibling class (P1), with the single named exception of `AlgorithmRegistry` (FR-3.1, FR-X.2).

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`, `14-directory-structure.md`
