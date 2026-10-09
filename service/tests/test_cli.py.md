# `test_cli.py`

**Package:** `service` · **Status:** pre-implementation test spec.

## What it verifies
- `init --recipe A|B|C` writes a file that passes `validate`; refuses to overwrite.
- `validate` returns exit 0 for Recipe A, B and C examples and exit 2 for each error rule E1 to E8 (one fixture per rule).
- `explain` output contains no secret values (CFG-5) and includes the config hash.
- `run` exits 3 when Redis or the PKCS#11 module is unreachable and never falls back to a weaker backend (CFG-3).

## Source docs
- `15-config-and-composition.md`
