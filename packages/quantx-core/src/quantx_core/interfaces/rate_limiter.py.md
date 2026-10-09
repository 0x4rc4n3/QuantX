# `rate_limiter.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Defines the `RateLimiter` `Protocol` — one of the eight foundational Layer-0 interfaces every algorithm-agile component above it is built against, never against a concrete implementation directly (P1).

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/interfaces/`
- **Depends on:** nothing — this is a foundational `Protocol`, Layer 0's own contract.
- **Imported by:** `in_memory_rate_limiter.py` (Layer 0 impl); `session_orchestrator.py` (Layer 4, two instances), `totp_provider.py` (Layer 5, its own instance per FR-5.2), `push_authenticator.py` (Layer 5, its own instance per SR-5)

## Docstring contract
- **Layer:** 0
- **Depends on:** Nothing internal.
- **Implements:** `allow(identity_key: str) -> bool` — `True` if the caller is under limit (and the attempt is counted), `False` if the limit has already tripped
- **Outside:** Choosing *which* identity key(s) to gate on, and how many independent limiter instances to wire (per-identity, global, TOTP-specific, push-issuance-specific) — that's each caller's composition choice (FR-4.4, FR-5.2, SR-5).
- **Inside:** A single check-and-count method; independence between limiter instances is achieved by constructing separate `RateLimiter` objects, not by parameters on this interface.
- **Security notes:** FR-4.4 — both a per-identity and a global `RateLimiter` gate challenge issuance and verification, as two independently-constructed instances of this same interface.

## Required behavior
- `RateLimiter` is a `typing.Protocol` defining `allow(identity_key) -> bool`.
- FR-4.4: both a per-identity and a global `RateLimiter` gate challenge issuance and verification — achieved by wiring two separate instances, never by adding a second parameter to `allow()`.
- FR-5.2 / SR-5: TOTP verification and push-notification issuance each get their own independent `RateLimiter` instance, never sharing state with the Layer 4 session limiter.

## Inputs / outputs
- **In/Out:** defined per-method by the `Protocol`; see `Docstring contract` above.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- **(foundational, cross-cutting).** Every limiter used in the system — session, TOTP, push-issuance — is a separate instance of this one interface; independence between them is a wiring property, not something this interface enforces by itself.

## Mandatory tests this must pass
- No dedicated test file — a `Protocol` has no behavior of its own to test; conformance is exercised indirectly by every concrete implementation's own test suite.

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Any concrete implementation — those live in `impls/`.

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`
