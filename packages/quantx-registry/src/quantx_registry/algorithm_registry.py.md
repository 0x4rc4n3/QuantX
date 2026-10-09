# `algorithm_registry.py`

**Package:** `quantx-registry` · **Layer:** 3 — Registry · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

**This file is `GATE_REVIEW_REQUIRED` (`10-security-requirements.md`, FR-3.1).** It may not be called "production-ready" in any doc, README, or client material until someone *other than its author* has reviewed it and the sign-off is logged in `docs/adr/algorithm_registry.md`. An AI coding agent completing this file is the author for this purpose.

## Purpose
The single place in the codebase allowed to import every Layer-1 adapter directly (FR-3.1) — resolves a named registry role (e.g. `session-auth`, `session-auth-pqc-only`) to a fully-wired `SignatureCombiner`/`KEMCombiner` pair plus a `required_mode`, loaded from YAML.

## Part of / dependency graph
- **Package:** `quantx-registry`, `src/quantx_registry`
- **Depends on:** Every Layer-1 adapter (`ed25519_adapter.py` through `ml_kem_1024_adapter.py`) — the one named exception to FR-X.2's no-sibling-import rule; `signature_combiner.py`, `kem_combiner.py` (Layer 2); `registry_role.py`, `registry_config_loader.py`, `registry_config_signature.py` (this package)
- **Imported by:** `default_setup.py` (Layer 4, Recipe A wiring); `service/src/quantx_service/wiring.py` (the REST sidecar's composition root)
- **Sideways-import note:** This is the one named exception to "no component above Layer 1 imports a sibling concrete class" (FR-X.2) — explicitly called out, not an oversight.

## Docstring contract
- **Layer:** 3
- **Depends on:** Every Layer-1 adapter (exception to FR-X.2); `SignatureCombiner`, `KEMCombiner` (Layer 2); this package's own role/loader/signature files
- **Implements:** `resolve(role_name: str) -> (SignatureCombiner | KEMCombiner, required_mode)` or equivalent
- **Outside:** Loading/parsing the YAML file itself (`registry_config_loader.py`); verifying the config's signature (`registry_config_signature.py`); defining what a role *is* as a value (`registry_role.py`).
- **Inside:** Resolving a role name to a concrete, constructed combiner pair, using adapters it alone is permitted to import directly.
- **Security notes:** FR-3.3: unsigned config only for `allow_unsigned=True` dev/demo use; the signed-config path is what any non-dev deployment (Recipe B/C) uses and rejects unsigned config by default.

## Required behavior
- Is the only file in the codebase permitted to import every Layer-1 adapter directly (FR-3.1) — every other component above Layer 1 reaches an algorithm only through a role this class resolves.
- Registry roles map a name to a concrete algorithm pairing plus a `required_mode`, loaded from YAML (FR-3.2).
- Dev/demo config may load unsigned (`allow_unsigned=True`) — but this is an explicit, opt-in flag, never the default (FR-3.3).
- The signed-config path is built from the start and is what any non-dev deployment (Recipe B/C) uses — it rejects unsigned config outright, at load time, not at first use (FR-3.3, `13-error-and-edge-cases.md`).
- A registry role referencing an algorithm adapter that isn't registered/available fails at load/startup time, fail-fast — not at first use (`13-error-and-edge-cases.md`).
- Resolves every registry role to a correctly-wired combiner (`02-build-order.md` Layer-3 definition of done).

## Inputs / outputs
- **In:** a role name (`str`) plus a loaded/verified config (via `registry_config_loader.py` and, unless `allow_unsigned=True`, `registry_config_signature.py`).
- **Out:** a constructed `SignatureCombiner`/`KEMCombiner` (or both) wired to the role's algorithm pairing, plus the role's `required_mode`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- An unsigned `AlgorithmRegistry` config is loaded in a context that requires signing (Recipe B/C) → rejected at load time — the deployment does not start in a half-configured state (`13-error-and-edge-cases.md`).
- A registry role references an algorithm adapter that isn't registered/available → fails at load/startup time, fail-fast.
- Two verifiers in the same deployment configured with different `required_mode` values for the same role → a config error caught at registry-load time, since `AlgorithmRegistry` roles are the single source of truth per role name.

## Security notes
- **FR-3.1.** The one place allowed to import every Layer-1 adapter — this containment is what makes FR-X.2's sibling-import ban meaningful elsewhere (there's exactly one named exception, not an unbounded set).
- **FR-3.3.** Signed-config-by-default for non-dev deployments.
- This is a `GATE_REVIEW_REQUIRED` component (`10-security-requirements.md`'s review-gates list).

## Mandatory tests this must pass
- `tests/test_algorithm_registry.py`
- `tests/security/test_unsigned_config_rejected_when_signing_required.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P2.** One algorithm per adapter file, forever.
- **P3.** Exactly one `SignatureCombiner`, one `KEMCombiner` — pairing is runtime wiring, not a new class.
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Parsing YAML itself — `registry_config_loader.py`.
- Verifying the config's cryptographic signature — `registry_config_signature.py`.
- Defining what a role's data shape is — `registry_role.py`.

## Source docs
`04-functional-requirements.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`, `02-build-order.md`, `09-auth-and-authorization.md`
