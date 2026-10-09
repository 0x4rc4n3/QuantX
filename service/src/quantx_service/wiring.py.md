# `wiring.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The sidecar's composition root — constructs `AlgorithmRegistry`, `SessionOrchestrator`, and every backend the configured recipe needs, exactly once, at startup. The REST-sidecar analogue of `default_setup.py`, but built from `config.py` rather than hardcoded Recipe-A defaults.

## Part of / dependency graph
- **Package:** `service`, `src/quantx_service`
- **Depends on:** `config.py` (this package); `AlgorithmRegistry` (Layer 3), `SessionOrchestrator` (Layer 4), and whichever Layer 0/6 backends the configured recipe specifies
- **Imported by:** `main.py`, `routers/*.py` (this package, via dependency injection)

## Docstring contract
- **Layer:** sidecar
- **Depends on:** `config.py` (this package); `AlgorithmRegistry`, `SessionOrchestrator` (Layers 3-4); configured backends
- **Implements:** `build_app_dependencies(config) -> AppDependencies` (or equivalent, wired via FastAPI's dependency-injection system)
- **Outside:** Request handling — routers' job.
- **Inside:** One-time object-graph construction at startup.
- **Security notes:** This is the one file above Layer 3 that constructs an `AlgorithmRegistry` directly for the sidecar — routers receive it via dependency injection, never construct their own.

## Required behavior
- Builds each replaceable part from the validated `quantx.yaml` selection (`docs/15-config-and-composition.md`). Any selection that cannot be built raises a typed error and the process exits non-zero. It never substitutes a weaker part (CFG-3).
- Constructs the full object graph (`AlgorithmRegistry`, `SessionOrchestrator`, backends) exactly once at startup, from `config.py`'s values.
- Routers receive dependencies via FastAPI's DI system, sourced from this file — no router constructs its own `AlgorithmRegistry`/`SessionOrchestrator`.

## Inputs / outputs
- **In:** a `ServiceConfig` from `config.py`.
- **Out:** the constructed object graph, exposed via FastAPI dependency injection.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- *(not specified in the available source docs — flag for human review.)*

## Security notes
- Sole sidecar-level composition root — keeps every router's constructor dependency-inverted against the interfaces those library objects expose, per P1.

## Mandatory tests this must pass
- Exercised indirectly via `service/tests/conftest.py`'s test-client app construction.

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.

## Explicitly out of scope for this file
- Request handling.
- Config parsing itself — `config.py`.

## Source docs
`06-system-architecture.md`, `04-functional-requirements.md`
