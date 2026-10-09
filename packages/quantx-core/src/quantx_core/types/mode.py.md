# `mode.py`

**Package:** `quantx-core` · **Layer:** 0 — Foundational interfaces · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Defines `Mode`, the enum formally typing the three modes QuantX ever runs in — `HYBRID`, `PQC_ONLY`, `CLASSICAL_ONLY`. This is the type `required_mode` is expressed in everywhere it appears, so "mode" is never a bare string anywhere in the codebase.

## Part of
- **Depends on:** nothing internal to QuantX (foundational value type).
- **Imported by:** `signature_mode_enforcement.py`, `kem_hkdf_binding.py`/`kem_combiner.py` (Layer 2); `registry_role.py`, `algorithm_registry.py` (Layer 3); `challenge_record.py`, `session_orchestrator.py` (Layer 4); `service/src/quantx_service/routers/verify_router.py` (maps the wire `declared_mode` string onto this type)

## Shape
- `Mode` — a `str`-backed `Enum` (or equivalent) with exactly three members: `HYBRID`, `PQC_ONLY`, `CLASSICAL_ONLY` (`00-index.md` decisions register, D2).
- Immutable — enum members are singletons by construction; no mutable state.
- `HYBRID` is the default posture; `PQC_ONLY`/`CLASSICAL_ONLY` are explicit server-side opt-ins, never client-negotiated (D2, SR-1).

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Two verifiers in the same deployment configured with different `required_mode` values for the same role is a config error caught at registry-load time, not a runtime ambiguity this type resolves at the value level.

## Non-negotiable principles that apply
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`00-index.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`, `04-functional-requirements.md`
