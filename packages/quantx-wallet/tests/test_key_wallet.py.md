# `test_key_wallet.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Verifies `KeyWallet` correctly delegates `store`/`retrieve` to whichever backend it's constructed with, and propagates backend errors unchanged.

## Part of / dependency graph
- **Package:** `quantx-wallet`, `tests/`
- **Depends on:** `key_wallet.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 6
- **Depends on:** `key_wallet.py`
- **Implements:** pytest test functions.
- **Outside:** Backend-specific storage mechanics — `backends/` tests.
- **Inside:** Delegation and error-propagation behavior.
- **Security notes:** Confirms FR-6.1 at the unit level.

## Required behavior
- `store`/`retrieve` calls are forwarded to the constructor-injected backend unchanged.
- A `BackendUnavailableError` raised by the backend propagates through `KeyWallet` unmasked.

## Inputs / outputs
- **In:** a mock/fake backend.
- **Out:** pass/fail.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- No specific `SR-x` item applies directly to this file beyond the general foundational rules in `10-security-requirements.md` (no in-house primitive crypto, all state through `KeyValueStore`, `Clock` always injected).

## Mandatory tests this must pass
- This file is itself the unit test for `key_wallet.py`.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Backend-specific mechanics.

## Source docs
`04-functional-requirements.md`
