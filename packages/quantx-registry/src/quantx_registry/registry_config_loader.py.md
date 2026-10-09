# `registry_config_loader.py`

**Package:** `quantx-registry` · **Layer:** 3 — Registry · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Loads the `AlgorithmRegistry` YAML config file using `yaml.safe_load` only — never `yaml.load` — and parses it into `RegistryRole` values.

## Part of / dependency graph
- **Package:** `quantx-registry`, `src/quantx_registry`
- **Depends on:** `registry_role.py` (this package); PyYAML's `safe_load`
- **Imported by:** `algorithm_registry.py` (this package)

## Docstring contract
- **Layer:** 3
- **Depends on:** `RegistryRole` (this package), PyYAML
- **Implements:** `load(path) -> list[RegistryRole]` (pre-signature-verification, raw parse)
- **Outside:** Verifying the config's signature — `registry_config_signature.py`'s job; this file only parses structure.
- **Inside:** Safe YAML parsing and validation into `RegistryRole` values.
- **Security notes:** Uses `yaml.safe_load` exclusively (`06-system-architecture.md`'s tech-stack table) — never `yaml.load`, which can execute arbitrary Python objects during deserialization.

## Required behavior
- Parses YAML exclusively via `yaml.safe_load` — never `yaml.load` (`06-system-architecture.md`).
- Fails fast at load time if a role references an algorithm adapter that isn't registered/available — not deferred to first use (`13-error-and-edge-cases.md`).
- Does not itself decide whether the config's signature is valid — that's `registry_config_signature.py`'s job, called by `algorithm_registry.py` separately unless `allow_unsigned=True`.

## Inputs / outputs
- **In:** a file path to a YAML config.
- **Out:** a list of parsed `RegistryRole` values, or an explicit load-time failure.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- A registry role references an algorithm adapter that isn't registered/available → fails at load/startup time, fail-fast (`13-error-and-edge-cases.md`).

## Security notes
- **(secrets & config management, `10-security-requirements.md`).** `yaml.safe_load` only, never `yaml.load` — an unpinned/unsafe YAML load path in a crypto-adjacent config loader is a supply-chain-class risk, not just a style preference.

## Mandatory tests this must pass
- `tests/test_registry_config_loader.py`

## Non-negotiable principles that apply
- **P6.** No docstring claims a capability the code doesn't have.

## Explicitly out of scope for this file
- Signature verification — `registry_config_signature.py`.

## Source docs
`06-system-architecture.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
