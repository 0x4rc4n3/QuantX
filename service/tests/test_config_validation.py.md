# `test_config_validation.py`

**Package:** `service` · **Status:** pre-implementation test spec.

## What it verifies
- Every rule in the table in `docs/15-config-and-composition.md` (E1 to E8, W1 to W9) has at least one passing and one failing fixture.
- A blocked option (`slh-dsa`) and an interface-only option (`anonymous`) are refused (CFG-6).
- A literal under a secret-like key is refused (E4).
- The same validator is used by the CLI, startup and the slicer (CFG-2): one import path, checked by a lint test.

## Source docs
- `15-config-and-composition.md`
