# `device_linker.py`

**Package:** `quantx-wallet` · **Layer:** 6-7 — Key custody & recovery · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Handles device-pairing tokens for recovery and enrollment so that a pairing token can't be replayed (`02-build-order.md` Layer-7 done criterion). Tokens are 256-bit random values, single use through `ReplayStore`, with a 10-minute expiry from the injected `Clock` (D-015).

## Part of / dependency graph
- **Package:** `quantx-wallet`, `src/quantx_wallet`
- **Depends on:** `quantx_core.interfaces.replay_store.ReplayStore` (Layer 0); `quantx_core.interfaces.key_value_store.KeyValueStore` (Layer 0, per FR-0.2, for any pairing-token state)
- **Imported by:** Integrating-application recovery flows.

## Docstring contract
- **Layer:** 6-7
- **Depends on:** `ReplayStore`, `KeyValueStore` (Layer 0)
- **Implements:** `issue_pairing_token(subject_id) -> str`; `consume_pairing_token(token) -> bool` (D-015)
- **Outside:** Any specific device-to-device transport for delivering the pairing token.
- **Inside:** Pairing-token issuance and single-use consumption.
- **Security notes:** Consume-once via `ReplayStore`, same discipline as every other replay-sensitive credential (SR-11's spirit, applied here by `02-build-order.md`'s stated done-criterion even though device-pairing isn't separately enumerated in the SR register).

## Required behavior
- Device-pairing tokens can't be replayed (`02-build-order.md` Layer-7 done criterion) — enforced via `ReplayStore` consume-once semantics, consistent with every other replay-sensitive credential in the system.
- Any durable state (pending pairing tokens) goes through `KeyValueStore`, per FR-0.2 — no ad hoc in-process cache.

## Inputs / outputs
- **In:** `issue_pairing_token`: `subject_id`. `consume_pairing_token`: a token.
- **Out:** `issue_pairing_token`: a token. `consume_pairing_token`: `bool`, single-use.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A subject loses access to their key custody entirely (device lost, no backup codes left) → out of QuantX's scope — an identity-proofing/support-process decision for the integrating application, not something this file (or QuantX generally) solves cryptographically (`13-error-and-edge-cases.md`).

## Security notes
- Consume-once discipline mirroring SR-11's pattern, per `02-build-order.md`'s Layer-7 done criterion for this file.

## Mandatory tests this must pass
- `tests/test_device_linker.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.

## Explicitly out of scope for this file
- Cross-device transport for delivering the token.
- Recovery when no factor remains at all — explicitly out of QuantX's scope.

## Source docs
`02-build-order.md`, `13-error-and-edge-cases.md`
