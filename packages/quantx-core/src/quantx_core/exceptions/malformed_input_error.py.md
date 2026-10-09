# `malformed_input_error.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The explicit error a wire-format parser raises when input can't even be parsed enough to attempt verification — distinct from `Verifier.verify()` itself, which must catch this internally and return `False` rather than let it propagate (FR-0.1).

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/exceptions/`
- **Depends on:** Python's built-in `Exception`.
- **Imported by:** `signature_wire_format.py`, `kem_wire_format.py` (Layer 2, at the raw parsing stage, before a `Verifier`/`KEMProvider` is ever called) `(inferred: FR-0.1 is explicit that Verifier.verify() never raises; this exception type's existence implies it's used at the lower-level wire-parsing stage that verify() itself wraps and converts to False)`; The combiner classes internally, converting this into a `False`/rejection result before it ever reaches a caller of `verify()`/`decapsulate()`; `service/src/quantx_service/errors/malformed_request_error.py` maps a parse failure at the sidecar boundary to `400 malformed_request`

## Docstring contract
- **Layer:** 0
- **Depends on:** Nothing internal beyond the standard exception hierarchy.
- **Implements:** `MalformedInputError(Exception)` — a typed exception, no custom behavior beyond carrying a message and (where noted) structured context.
- **Outside:** Deciding when to raise it — that's every raising component's own concern.
- **Inside:** The exception type itself and its constructor shape.
- **Security notes:** **FR-0.1 / wire-parser fuzzing (mandatory test 5, `10-security-requirements.md`).** This is exactly the failure mode wire-parser fuzz tests target: a length-prefixed field claiming a length larger than the remaining buffer must raise this and be caught, never cause an out-of-bounds read (`13-error-and-edge-cases.md`).

## Required behavior
- `MalformedInputError` is a distinct, typed exception — never conflated with a generic `Exception` or `ValueError`, so callers (including the REST sidecar's error-mapping layer) can catch it specifically.
- Carries enough context in its message/attributes for a caller to log a useful diagnostic without needing to re-derive what failed `(inferred: exact attribute shape isn't specified in the docs)`.

## Inputs / outputs
- **In:** a human-readable message and any structured context the raising site provides.
- **Out:** nothing — it's raised, not returned.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **FR-0.1 / wire-parser fuzzing (mandatory test 5, `10-security-requirements.md`).** This is exactly the failure mode wire-parser fuzz tests target: a length-prefixed field claiming a length larger than the remaining buffer must raise this and be caught, never cause an out-of-bounds read (`13-error-and-edge-cases.md`).

## Mandatory tests this must pass
- Exercised indirectly by every test that asserts a specific failure mode raises this exception rather than a generic one or silently passing.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Deciding when to raise this — that's each raising component's own file.

## Source docs
`10-security-requirements.md`, `13-error-and-edge-cases.md`
