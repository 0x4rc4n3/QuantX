# `cli.py`

**Package:** `service` · **Layer:** REST sidecar (top-level, not under packages/) · **Status:** pre-implementation, spec for a file that does not exist yet.

## Purpose
The thin command line for configuration-driven composition (D-012): `quantx init`, `validate`, `explain`, `run`. All logic lives in `config.py` and `wiring.py`; this file parses arguments, calls them, prints results and sets exit codes.

## Part of / dependency graph
- **Package:** `service`, `src/quantx_service`
- **Depends on:** `config.py`, `wiring.py`, `main.py` (this package)
- **Imported by:** the `quantx` console script entry point

## Docstring contract
- **Layer:** sidecar
- **Depends on:** `config.py`, `wiring.py`, `main.py`
- **Implements:** `main(argv) -> int` with subcommands `init`, `validate`, `explain`, `run`
- **Outside:** Validation rules (`config.py`), object construction (`wiring.py`), request handling (routers).
- **Inside:** Argument parsing, printing, exit codes.
- **Security notes:** Never prints secret values; `explain` shows references and resolved class names only (CFG-5).

## Required behavior
- Exactly the commands, outputs and exit codes in `docs/15-config-and-composition.md` (CLI contract).
- `init` refuses to overwrite an existing file.
- `run` validates first, probes backends, then starts the app; any failure exits non-zero and never starts a weaker configuration (CFG-3).

## Inputs / outputs
- **In:** command-line arguments, a `quantx.yaml` file.
- **Out:** text on stdout/stderr and an integer exit code (0, 2, 3).

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- Missing config file: print the path searched, exit 2.
- Unknown subcommand: print usage, exit 2.
- Interrupt during `run`: clean shutdown, exit 0.

## Security notes
- Config contents are untrusted input: parse as data only (CFG-7).

## Mandatory tests this must pass
- `tests/test_cli.py`
- `tests/test_config_validation.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always.

## Explicitly out of scope for this file
- Validation rules and wiring.

## Source docs
- `15-config-and-composition.md`, `DECISIONS.md` (D-012)
