# `registry_role.py`

**Package:** `quantx-registry` · **Layer:** 3 — Registry · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The value type mapping a role name (e.g. `session-auth`, `session-auth-pqc-only`) to a concrete algorithm pairing and a `required_mode` (FR-3.2) — what `algorithm_registry.py` resolves a role name *to*.

## Part of
- **Depends on:** `quantx_core.types.mode.Mode`, `quantx_core.types.algorithm_id.AlgorithmId` (Layer 0)
- **Imported by:** `algorithm_registry.py`, `registry_config_loader.py` (this package)

## Shape
- `RegistryRole` — a frozen value type with fields for: role name (`str`), the algorithm pairing (one or two `AlgorithmId` values, per whether it's a signature or KEM role), and `required_mode: Mode`.
- Immutable once loaded from config — a role's meaning for a given deployment doesn't change at runtime.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A registry role references an algorithm adapter that isn't registered/available → fails at load/startup time (`13-error-and-edge-cases.md`).

## Non-negotiable principles that apply
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`04-functional-requirements.md`, `13-error-and-edge-cases.md`
