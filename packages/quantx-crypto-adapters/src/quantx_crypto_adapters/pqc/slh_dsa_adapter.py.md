# `slh_dsa_adapter.py`

**Package:** `quantx-crypto-adapters` · **Layer:** 1 — Algorithm adapters · **Status:** specified, **blocked on upstream** (D-006) — do not implement until `cryptography` ships SLH-DSA.

## Purpose
Will wrap `cryptography`'s (pyca) SLH-DSA (FIPS 205, hash-based) signature scheme behind the `Signer`/`Verifier` contract — a structurally different PQC signature family from ML-DSA, useful as a hedge against a lattice-specific break.

## Blocked on upstream (D-006)
- `cryptography` 48 has no SLH-DSA and upstream work had only started (Trail of Bits, 2026-06-30). Re-check the current `cryptography` release notes before unblocking; a later-release claim (e.g. 50.0.x) was not independently verified on 2026-10-03.
- **No substitute library.** `liboqs` is dropped project-wide (D-006); no other SLH-DSA implementation may stand in. This is an upstream-gated exception to D10/D12, like `AnonymousProofBackend`'s audit gate, not a schedule deferral.
- Until unblocked: `AlgorithmId.SLH_DSA` stays reserved, no adapter or `test_slh_dsa_adapter.py` is created, and the registry fails closed on any `AlgorithmId` with no registered adapter.
- Unblock criteria: a `cryptography` release exposing SLH-DSA on the backend QuantX ships against. Then this spec is revised to the pyca mapping (as in the ML-DSA adapters), the parameter set is chosen, and the adapter and test are built in the same pass.

## Part of / dependency graph
- **Package:** `quantx-crypto-adapters`, `src/quantx_crypto_adapters/pqc/`
- **Depends on:** `quantx_core.interfaces.signer.Signer` (Layer 0 interface this implements)
- **Imported by:** `algorithm_registry.py` (Layer 3) — the only place above Layer 1 allowed to import this directly (FR-3.1)
- **Size constraint:** ~30-60 lines target (FR-1.3); if it grows past that, the excess belongs in a different layer, not here.

## Docstring contract
- **Layer:** 1
- **Depends on:** `Signer` (Layer 0)
- **Implements:** `Signer` for SLH-DSA
- **Outside:** Any branching on algorithm family — this file handles exactly one algorithm and nothing else (FR-1.1, P2).
- **Inside:** SLH-DSA key generation, and the sign/verify operations, wrapping `cryptography` (pyca) — never a hand-rolled primitive (D1).
- **Security notes:** No `SR-x` item is specific to this adapter beyond FR-0.1. The PQC backend statement (D-006) will apply once built.

## Required behavior
- Implements `generate_keypair`, `sign(message) -> bytes`, and satisfies `Verifier.verify(message, signature) -> bool` for SLH-DSA only (FR-1.1).
- Will wrap `cryptography` (pyca) — never a hand-rolled implementation (D1).
- `verify()` catches any internal exception and returns `False` — never raises (FR-0.1).

## Inputs / outputs
- **In:** `sign`: a message (`bytes`). `verify`: message + signature (`bytes`, `bytes`).
- **Out:** `sign`: an SLH-DSA signature (hash-based signatures are typically larger than lattice-based ML-DSA `(inferred — the docs don't give SLH-DSA's specific size, only ML-DSA-65's ~3.3KB and ML-KEM-768's ~1.1KB as the budget's reference figures)`). `verify`: `bool`, never raises.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Signature/KEM bytes are malformed or truncated → `verify()`/`decapsulate()` catches the parse/crypto-library failure internally and returns `False` (or fails closed) — never raises (FR-0.1, `13-error-and-edge-cases.md`).

## Security notes
- No `SR-x` item is specific to this adapter beyond FR-0.1. The PQC backend statement (D-006) will apply once built.
- Any material referencing this adapter states it is not yet available, and why (D-006).

## Mandatory tests this must pass
- `tests/pqc/test_slh_dsa_adapter.py`
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
