# `test_sr_02_merkle_proof_actually_walks_path_to_root.py`

**Package:** `quantx-zkp` · **Layer:** 9 — Anonymous membership proofs · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The mandatory test that would catch a stub verifier that just checks the leaf exists in a lookup table instead of actually walking the path to the root — SR-2's exact concern.

## Part of / dependency graph
- **Package:** `quantx-zkp`, `tests/security/`
- **Depends on:** `merkle_membership_proof.py`; `merkle_tree.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 9
- **Depends on:** `merkle_membership_proof.py`, `merkle_tree.py`
- **Implements:** The mandatory automated security test for SR-2.
- **Outside:** General structural round-trip correctness — `test_merkle_membership_proof.py`.
- **Inside:** A scenario specifically designed to fail a lookup-table-only stub while passing a real path-walking verifier.
- **Security notes:** This file **is** the SR-2 enforcement check.

## Required behavior
- Construct a proof where the claimed member is genuinely NOT part of the tree the `claimed_root` corresponds to, but craft the path such that a naive "does the leaf exist somewhere" check might be fooled (e.g. the member exists in a *different* tree/root).
- Confirm `verify()` rejects this — because it recomputes the root from `member` + `path` and compares to `claimed_root`, a mismatched tree fails regardless of whether the member exists elsewhere.
- This is the literal scenario `10-security-requirements.md` names: "a verifier that just checks the leaf exists in a lookup table" must be caught by this test.

## Inputs / outputs
- **In:** a proof for a member of a different tree than the claimed root.
- **Out:** must reject — a release blocker if this ever returns `True`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A membership-proof verifier is asked to verify a proof for a non-member → the walked path does not reproduce `claimed_root`, so verification fails (`13-error-and-edge-cases.md`).

## Security notes
- **SR-2.**

## Mandatory tests this must pass
- This file *is* the mandatory SR-2 test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- General round-trip correctness — separate file.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`
