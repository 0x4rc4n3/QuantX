# `config.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Loads sidecar configuration (which recipe/backends to wire, TLS requirements, rate-limit thresholds) from environment/config file.

## Part of / dependency graph
- **Package:** `service`, `src/quantx_service`
- **Depends on:** Nothing internal — reads environment/config file.
- **Imported by:** `wiring.py` (this package)

## Docstring contract
- **Layer:** sidecar
- **Depends on:** Nothing internal.
- **Implements:** `load_config() -> ServiceConfig`
- **Outside:** Actually constructing library objects from the config — `wiring.py`'s job.
- **Inside:** Reading and validating configuration values.
- **Security notes:** Any secret material (signing keys, backend credentials) referenced here is loaded per `10-security-requirements.md`'s secrets-management rules, never hardcoded.

## Required behavior
- Loads `quantx.yaml` (or environment) to select the recipe and every replaceable part, backend connection references, TLS enforcement mode and rate-limit thresholds. The schema, option statuses and validation rules are specified in `docs/15-config-and-composition.md` (draft v1). Proxy-trust and TLS-termination settings are still open (S-004).
- Never hardcodes secret material — configuration values reference where secrets live (environment variable, secret manager), not the secrets themselves.

## Inputs / outputs
- **In:** environment variables / a config file.
- **Out:** a `ServiceConfig` value.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- TLS is terminated by this service's own process (D-016). Configuration that points at an external proxy for TLS is rejected at startup.

## Security notes
- No secret material hardcoded — referenced from environment/secret manager only (`10-security-requirements.md`).

## Mandatory tests this must pass
- Exercised indirectly via `service/tests/conftest.py`'s app construction.

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Constructing library objects — `wiring.py`.

## Source docs
`10-security-requirements.md`, `06-system-architecture.md`
