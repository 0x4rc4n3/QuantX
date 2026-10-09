# `test_unsigned_config_rejected_when_signing_required.py`

**Package:** `quantx-registry` · **Layer:** 3 — Registry · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Confirms that loading an unsigned config in a context that requires signing (Recipe B/C, `allow_unsigned=False`) is rejected at load time — the deployment never starts in a half-configured state.

## Part of / dependency graph
- **Package:** `quantx-registry`, `tests/security/`
- **Depends on:** `algorithm_registry.py`; `registry_config_signature.py`
- **Imported by:** Nothing — a test file is a leaf.

## Docstring contract
- **Layer:** 3
- **Depends on:** `algorithm_registry.py`, `registry_config_signature.py`
- **Implements:** The mandatory foundational test for FR-3.3's signed-by-default rule.
- **Outside:** Testing the signature math itself — that's `test_registry_config_signature.py`.
- **Inside:** The load-time rejection behavior when signing is required and absent.
- **Security notes:** This file **is** the enforcement check for FR-3.3 / `09-auth-and-authorization.md`'s registry-level authorization model.

## Required behavior
- Construct an `AlgorithmRegistry` with `allow_unsigned=False` (the non-dev default).
- Attempt to load an unsigned config → must be rejected at load time, before the registry resolves any role, not deferred to first `resolve()` call.

## Inputs / outputs
- **In:** an unsigned config, `allow_unsigned=False`.
- **Out:** must raise/reject at load time; a release blocker if it silently loads.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- An unsigned `AlgorithmRegistry` config is loaded in a context that requires signing (Recipe B/C) → rejected at load time — the deployment does not start in a half-configured state (`13-error-and-edge-cases.md`).

## Security notes
- **FR-3.3.** The signed-config path is what any non-dev deployment uses.

## Mandatory tests this must pass
- This file *is* the mandatory test for this rule.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Explicitly out of scope for this file
- Signature math correctness — `test_registry_config_signature.py`.

## Source docs
`04-functional-requirements.md`, `09-auth-and-authorization.md`, `13-error-and-edge-cases.md`
