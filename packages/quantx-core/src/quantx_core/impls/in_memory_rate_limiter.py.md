# `in_memory_rate_limiter.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The reference `RateLimiter` implementation, backing Recipe A. Each independently-wired instance (per-identity, global, TOTP, push-issuance) is a separate object of this class.

## Part of / dependency graph
- **Package:** `quantx-core`, `src/quantx_core/impls/`
- **Depends on:** `quantx_core.interfaces.rate_limiter.RateLimiter` (Layer 0 interface this implements)
- **Imported by:** `default_setup.py` (Layer 4, Recipe A wiring), and any Layer 5 wiring that constructs its own TOTP/push-issuance limiter instances

## Docstring contract
- **Layer:** 0
- **Depends on:** `RateLimiter` (the interface it implements)
- **Implements:** InMemoryRateLimiter
- **Outside:** Anything not directly part of this one interface's contract.
- **Inside:** The concrete logic satisfying that contract.
- **Security notes:** **FR-4.4 / FR-5.2 / SR-5.** Backs every independently-required rate limiter instance in the system.

## Required behavior
- Implements `allow(identity_key) -> bool` over a fixed-window counter (D-015). Behavior at the window boundary is stated in the docstring and tested.
- State goes through an injected `KeyValueStore`, per FR-0.2/P5, rather than a private dict.
- Independence between limiter instances (per-identity vs. global vs. TOTP vs. push-issuance) is achieved purely by constructing separate instances — this class has no concept of "which limiter am I" beyond its own isolated state.

## Inputs / outputs
- **In:** `allow(identity_key)`.
- **Out:** `True`/`False`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A subject exceeds their per-identity rate limit → `429`-equivalent rejection, independent of the global limiter's state.
- Global rate limit is exceeded even though no single identity is over their own limit → still rejected — the two limiters are independent gates, not one merged counter (`13-error-and-edge-cases.md`).

## Security notes
- **FR-4.4 / FR-5.2 / SR-5.** Backs every independently-required rate limiter instance in the system.

## Mandatory tests this must pass
- `tests/impls/test_in_memory_rate_limiter.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P5.** No component invents its own persistence — everything stateful goes through `KeyValueStore`.
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Anything beyond the one interface this file implements — reference/dev implementations stay narrowly scoped.

## Source docs
`07-database-design.md`, `06-system-architecture.md`, `04-functional-requirements.md`
