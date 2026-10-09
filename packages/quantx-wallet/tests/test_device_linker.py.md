# `test_device_linker.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `DeviceLinker`'s pairing-token issuance and single-use consumption.

## Part of / dependency graph
- **Package:** `quantx-wallet`, `tests/`
- **Depends on:** `device_linker.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 6-7
- **Depends on:** `device_linker.py`
- **Implements:** pytest test functions.
- **Outside:** Cross-device transport.
- **Inside:** Pairing-token issuance/consumption.
- **Security notes:** Confirms the Layer-7 done criterion: pairing tokens can't be replayed.

## Required behavior
- A pairing token issued via `issue_pairing_token()` can be consumed exactly once.
- A second consumption attempt with the same token fails.

## Inputs / outputs
- **In:** a pairing token.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `device_linker.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Cross-device transport.

## Source docs
`02-build-order.md`
