# `test_default_setup_end_to_end_demo.py`

**Package:** `quantx-session` · **Layer:** 4 — Session · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Runs the full `default_setup() → start() → finish() → validate()` demo flow end-to-end — the first point in the build order where there's something worth showing someone outside the build (`02-build-order.md`).

## Part of / dependency graph
- **Package:** `quantx-session`, `tests/`
- **Depends on:** `default_setup.py`; `challenge_issuer.py`; `session_orchestrator.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 4
- **Depends on:** `default_setup.py` and everything it wires.
- **Implements:** The mandatory Layer-4 done-criterion demo, as a test.
- **Outside:** Recipe B/C — this test only exercises Recipe A.
- **Inside:** The full four-call flow.
- **Security notes:** Every mandatory security test applicable at this layer must pass against this flow before Layer 4 is considered done (`02-build-order.md`).

## Required behavior
- Call `default_setup()`, then `start(subject_id)`, sign the returned challenge with a real test keypair, call `finish(challenge_id, signed_response)`, then `validate(token)`.
- The full flow succeeds end-to-end for a genuine subject.
- This is the literal Layer-4 definition of done per `02-build-order.md`: "that full flow works, every mandatory security test ... passes against it, and Layers 0-2 have cleared outside review."

## Inputs / outputs
- **In:** none beyond what `default_setup()` provides.
- **Out:** pass/fail for the full flow.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file *is* the mandatory Layer-4 end-to-end demo test.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Adversarial/security-negative scenarios — those live in `security/` and in `quantx-combiners`'s own security suite.

## Source docs
`02-build-order.md`, `01-product-requirements.md`, `03-user-stories-and-flows.md`
