# `merkle_membership_proof.py`

**Package:** `quantx-zkp` · **Layer:** 9 — Anonymous membership proofs · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`, SR-2).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/merkle_and_anonymous_proof.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
The verifier that actually walks a claimed membership path to the root and checks it against the tree's real root — not a stub that just checks the leaf exists in a lookup table (FR-9.1, SR-2, the single most safety-critical line in this whole package).

## Part of / dependency graph
- **Package:** `quantx-zkp`, `src/quantx_zkp`
- **Depends on:** `merkle_tree.py` (this package)
- **Imported by:** Any surface presenting a membership proof to a relying party (integrating-application concern) `(inferred consumer)`

## Docstring contract
- **Layer:** 9
- **Depends on:** `MerkleTree` (this package)
- **Implements:** `verify(member, path, claimed_root) -> bool` — walks the path, computes the resulting root, compares
- **Outside:** Tree construction itself — `merkle_tree.py`'s job.
- **Inside:** Actually recomputing the root from `member` + `path` and comparing to `claimed_root`.
- **Security notes:** SR-2 in full: the verifier must actually walk the path to the root — a verifier that just checks the leaf exists in a lookup table is *not* a zero-knowledge membership proof and is exactly the failure mode SR-2 exists to catch.

## Required behavior
- `verify()` recomputes the root by walking `path`'s sibling hashes up from `member`, and compares the result to `claimed_root` — it does not merely check that `member` exists in some server-side lookup table (FR-9.1, SR-2).
- Any surface presenting a `MerkleMembershipProof` states the non-anonymity caveat plainly: this only proves group membership, it does not itself provide unlinkability/anonymity guarantees beyond that (FR-9.3) — this is a docstring/documentation obligation on every consumer, not a runtime check this file performs.

## Inputs / outputs
- **In:** `member`, `path` (sibling hashes), `claimed_root`.
- **Out:** `bool` — `True` only if walking the path from `member` actually produces `claimed_root`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A membership-proof verifier is asked to verify a proof for a non-member → the walked path does not reproduce `claimed_root`, so verification fails — never a shortcut lookup-table check standing in for actually walking the path (SR-2, `13-error-and-edge-cases.md`).

## Security notes
- **SR-2.** The verifier must actually walk the path to the root. This is explicitly the property the mandatory security test for this file exists to catch a stub implementation of.
- **FR-9.3.** Non-anonymity caveat obligation on consumers (documentation, not this file's runtime behavior).

## Mandatory tests this must pass
- `tests/test_merkle_membership_proof.py`
- `tests/security/test_sr_02_merkle_proof_actually_walks_path_to_root.py`

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Tree construction — `merkle_tree.py`.
- Providing unlinkability/anonymity beyond group membership — that's `anonymous_proof_backend.py`'s (currently unbuilt) job, not this file's.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
