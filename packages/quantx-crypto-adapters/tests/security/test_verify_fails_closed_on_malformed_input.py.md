# `test_verify_fails_closed_on_malformed_input.py`

**Package:** `quantx-crypto-adapters` · **Layer:** 1 — Algorithm adapters · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The mandatory FR-0.1 enforcement test, parametrized across all eight Layer-1 adapters: `verify()`/`decapsulate()` must catch any internal failure and return `False`/fail closed, never raise.

## Part of / dependency graph
- **Package:** `quantx-crypto-adapters`, `tests/security/`
- **Depends on:** Every adapter in `classical/` and `pqc/` (parametrized)
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 1
- **Depends on:** Every Layer-1 adapter.
- **Implements:** The mandatory automated test for FR-0.1.
- **Outside:** Round-trip success-path testing — that's each per-adapter test file's job.
- **Inside:** Malformed/truncated/adversarial input against every adapter's verify/decapsulate path.
- **Security notes:** This file **is** the FR-0.1 enforcement check, for every adapter at once.

## Required behavior
- Parametrized across the seven buildable adapters (Ed25519, ECDSA-P256, ML-DSA-65, ML-DSA-87, X25519, ML-KEM-768, ML-KEM-1024). SLH-DSA joins when unblocked (D-006).
- For each: feed malformed/truncated signature or ciphertext bytes into `verify()`/`decapsulate()` and confirm it returns `False`/fails closed rather than raising.

## Inputs / outputs
- **In:** deliberately malformed bytes per adapter.
- **Out:** pass/fail; failure here is a release blocker (FR-0.1 is a Layer-1 done-criterion per `02-build-order.md`).

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Signature/KEM bytes are malformed or truncated → caught internally, returns `False` — never raises (FR-0.1, `13-error-and-edge-cases.md`).

## Security notes
- **FR-0.1.** `Verifier.verify()` (and, by the same fail-closed principle, `KEMProvider.decapsulate()`) never raises on malformed input — this file is the enforcement test, across every adapter, one parametrized suite.

## Mandatory tests this must pass
- This file *is* the mandatory FR-0.1 test.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Success-path round-trip testing — see each adapter's own test file.

## Source docs
`04-functional-requirements.md`, `13-error-and-edge-cases.md`, `02-build-order.md`
