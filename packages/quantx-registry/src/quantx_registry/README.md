# `quantx_registry` — package source root

## What this is
`AlgorithmRegistry` (FR-3.1, `GATE_REVIEW_REQUIRED`) and its three supporting files: the role value type, the YAML loader, and the config-signing logic.

## Part of
`quantx-registry`, Layer 3.

## Contains
- `algorithm_registry.py` — the one file allowed to import every Layer-1 adapter (FR-3.1)
- `registry_role.py` — role → (pairing, required_mode) value type
- `registry_config_loader.py` — `yaml.safe_load` only, never `yaml.load`
- `registry_config_signature.py` — sign / verify the config file itself

## Why divided this way
Loading, signing, and resolving are three independently-testable concerns (`14-directory-structure.md`'s atomicity rule) — a change to the YAML schema shouldn't require touching signature-verification logic, and vice versa.

## Dependency rules
- Only `algorithm_registry.py` imports Layer-1 adapters directly (FR-3.1, the sole exception to FR-X.2).
- `registry_config_loader.py` and `registry_config_signature.py` never import Layer-1 adapters — they operate purely on config structure/bytes.

## Source docs
`04-functional-requirements.md`, `14-directory-structure.md`
