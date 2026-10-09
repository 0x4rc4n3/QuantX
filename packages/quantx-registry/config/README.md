# `config/` — example registry configuration

## What this is
A non-authoritative example `AlgorithmRegistry` YAML config, for dev/demo use with `allow_unsigned=True`.

## Part of
`quantx-registry`, Layer 3.

## Contains
- `algorithm_registry.example.yaml` — example role definitions

## Why divided this way
Kept separate from `src/` since it's data, not code, and separate from any specific client's real (signed, secret) production config, which never belongs in this repo.

## Dependency rules
- Loaded only via `registry_config_loader.py`'s `yaml.safe_load` path — never read by any other mechanism.

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`
