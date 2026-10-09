# `anonymous_proof_backend.py`

**Package:** `quantx-zkp` · **Layer:** 9 — Anonymous membership proofs · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`'s review gates).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/merkle_and_anonymous_proof.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
The placeholder for true anonymous (zk-SNARK-class) proofs — raises `NotImplementedError` until a funded, scoped external audit happens (FR-9.2, D9). This file's entire job is to be honest that this capability doesn't exist yet, not to approximate it.

## Part of / dependency graph
- **Package:** `quantx-zkp`, `src/quantx_zkp`
- **Depends on:** Nothing — deliberately unimplemented.
- **Imported by:** Any caller attempting true anonymous proofs gets `NotImplementedError` — no production caller should be wired to expect success from this class yet.

## Docstring contract
- **Layer:** 9
- **Depends on:** Nothing.
- **Implements:** The interface remains intentionally unimplemented and raises `NotImplementedError` for any attempted anonymous-proof operation. The replacement architecture contract does not authorize a concrete proof method until a vetted construction, exact API, test vectors, and independent review are approved.
- **Outside:** Merkle-based group-membership proofs — `merkle_membership_proof.py` already provides that, honestly scoped as non-anonymous.
- **Inside:** The explicit `NotImplementedError` and its explanatory message.
- **Security notes:** D9/FR-9.2: no attempt at a homegrown zk-SNARK — this stays unimplemented until a funded, scoped external audit happens, precisely because getting this wrong quietly would be far worse than not having it.

## Required behavior
- Raises `NotImplementedError` on every method until a funded, scoped external audit happens (FR-9.2, D9) — never a partial or "good enough for now" implementation.
- The `NotImplementedError`'s message states plainly why (no funded audit yet), so a caller understands this is a scoping decision, not a bug.

## Inputs / outputs
- **In:** any method call.
- **Out:** `NotImplementedError`, always, until this decision is revisited.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **FR-9.2 / D9.** No homegrown zk-SNARK implementation without a funded, scoped external audit — this file's entire reason for existing is to make that boundary explicit and impossible to silently work around.

## Mandatory tests this must pass
- `tests/test_anonymous_proof_backend_raises_not_implemented.py`

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Actually implementing anonymous proofs — blocked on a funded, scoped external audit (D9).

## Source docs
`00-index.md`, `04-functional-requirements.md`
