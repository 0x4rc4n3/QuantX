# `test_anonymous_proof_backend_raises_not_implemented.py`

**Package:** `quantx-zkp` · **Layer:** 9 — Anonymous membership proofs · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms `AnonymousProofBackend` raises `NotImplementedError` on every method call — guards against a future contributor accidentally shipping a partial implementation without revisiting the D9 funded-audit gate.

## Part of / dependency graph
- **Package:** `quantx-zkp`, `tests/`
- **Depends on:** `anonymous_proof_backend.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 9
- **Depends on:** `anonymous_proof_backend.py`
- **Implements:** The mandatory test guarding D9's unimplemented-by-design state.
- **Outside:** Merkle-based proofs — separate package concern.
- **Inside:** Confirming every method raises `NotImplementedError`.
- **Security notes:** This file is what would catch a future accidental partial implementation slipping past D9's gate.

## Required behavior
- Every public method on `AnonymousProofBackend` raises `NotImplementedError` when called.

## Inputs / outputs
- **In:** any method call.
- **Out:** must always raise `NotImplementedError`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **D9 / FR-9.2.** This test is the tripwire for D9's funded-audit gate being silently bypassed by a future partial implementation.

## Mandatory tests this must pass
- This file *is* the mandatory test for this rule.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Anything about `merkle_membership_proof.py`.

## Source docs
`00-index.md`, `04-functional-requirements.md`
