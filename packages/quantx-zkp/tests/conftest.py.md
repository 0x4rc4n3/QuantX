# `conftest.py`

**Package:** `quantx-zkp` · **Layer:** 9 — Anonymous membership proofs · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Shared fixtures for zkp tests — a built `MerkleTree` over a sample member set, with genuine paths for both a member and a non-member.

## Part of / dependency graph
- **Package:** `quantx-zkp`, `tests/`
- **Depends on:** `merkle_tree.py`
- **Imported by:** Every test file in this package, implicitly.

## Docstring contract
- **Layer:** 9
- **Depends on:** `merkle_tree.py`
- **Implements:** pytest fixtures.
- **Outside:** Assertions.
- **Inside:** Fixture construction.
- **Security notes:** The non-member-path fixture is a precondition for `test_sr_02_merkle_proof_actually_walks_path_to_root.py`.

## Required behavior
- Provides a built `MerkleTree` and genuine sibling-hash paths for both a member and, where meaningful, a crafted non-member scenario.

## Inputs / outputs
- **In:** nothing.
- **Out:** fixture objects.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- Exercised implicitly by every test file in this package.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Assertion logic.

## Source docs
`14-directory-structure.md`
