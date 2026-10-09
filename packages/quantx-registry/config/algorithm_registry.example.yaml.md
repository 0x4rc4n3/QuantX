# `algorithm_registry.example.yaml`

**Location:** `packages/quantx-registry/config/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
An example, unsigned `AlgorithmRegistry` config — the shape `registry_config_loader.py` parses and `registry_role.py` values are constructed from. For dev/demo (`allow_unsigned=True`) use only; never a template for a real client's signed production config, which must not be committed to this repo.

## Required contents / behavior
- At least one role entry per the roles referenced elsewhere in this doc set — e.g. `session-auth` (HYBRID) and `session-auth-pqc-only` (PQC_ONLY) `(inferred exact role names — 04-functional-requirements.md names `session-auth` and `session-auth-pqc-only` as examples, not a mandated final list)`.
- Each role entry specifies: a role name, the algorithm pairing (one or two `AlgorithmId` values), and a `required_mode` (`HYBRID` / `PQC_ONLY` / `CLASSICAL_ONLY`).
- Parseable via `yaml.safe_load` only — no YAML tags requiring `yaml.load`'s unsafe deserialization (`06-system-architecture.md`).
- Not signed — this file is explicitly the `allow_unsigned=True` dev/demo path (FR-3.3); it must never be presented as, or used as, a production config.

## Non-negotiable principles that apply
- **P4.** Mode is a server-side construction fact, never trusted from wire data.
- **P6.** No docstring claims a capability the code doesn't have.

## Source docs
`04-functional-requirements.md`, `06-system-architecture.md`, `10-security-requirements.md`
