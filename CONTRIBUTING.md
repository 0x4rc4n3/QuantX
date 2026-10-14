# Contributing to QuantX

Thank you for your interest in contributing.

## Current Status

QuantX is in early implementation. The architecture and many package scaffolds exist. Core crypto-agile engine work is the highest priority.

## How to Contribute

1. Open an issue first for significant changes (design or large features).
2. Fork the repository and create a feature branch.
3. Follow the coding standards below.
4. Add or update tests for any new behavior.
5. Open a Pull Request against `main`.

## Development Setup

```bash
git clone https://github.com/0x4rc4n3/QuantX.git
cd QuantX
# Preferred: uv
uv sync
# Or standard pip/venv
python -m venv .venv
source .venv/bin/activate
pip install -e packages/*
```

## Coding Standards

- Python 3.11+
- Type hints required (`mypy --strict` target)
- Formatting and linting: `ruff format` + `ruff check`
- One public responsibility per module where practical
- Constructors take interfaces (Protocols), not concrete sibling classes
- No hand-rolled cryptography
- Docstrings should state what the component guarantees and what it does not

## Security-Sensitive Changes

Components marked `GATE_REVIEW_REQUIRED` (SignatureCombiner, KEMCombiner, ThresholdManager, etc.) require extra care. Document any security-relevant decisions in the PR and in `docs/adr/` when appropriate.

## Commit Style

Prefer Conventional Commits:

- `feat:`
- `fix:`
- `docs:`
- `test:`
- `refactor:`
- `chore:`

## Questions

Open a GitHub Discussion or Issue. For security issues, follow `SECURITY.md`.
