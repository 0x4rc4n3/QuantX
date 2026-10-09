# `registry_config_signature.py`

**Package:** `quantx-registry` · **Layer:** 3 — Registry · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Signs and verifies the `AlgorithmRegistry` config file itself, so that in any non-dev deployment (Recipe B/C), only whoever holds the signing key can change what `required_mode` means for a given role (`09-auth-and-authorization.md`).

## Part of / dependency graph
- **Package:** `quantx-registry`, `src/quantx_registry`
- **Depends on:** A `Signer`/`Verifier` pairing (Layer 0/1) used to sign/verify the config file's bytes, canonicalized via `Canonicalizer` before signing (FR-0.4)
- **Imported by:** `algorithm_registry.py` (this package), unless `allow_unsigned=True`

## Docstring contract
- **Layer:** 3
- **Depends on:** `Signer`/`Verifier` (Layer 0/1), `Canonicalizer` (Layer 0, FR-0.4)
- **Implements:** `sign(config_bytes) -> bytes`; `verify(config_bytes, signature) -> bool`
- **Outside:** Deciding whether signing is required for a given deployment — that's `algorithm_registry.py`'s `allow_unsigned` flag.
- **Inside:** The sign/verify operations over the canonicalized config file bytes.
- **Security notes:** FR-3.3 / SR-1-adjacent: whoever holds the signing key is functionally the only party who can change registry roles for a production deployment (`09-auth-and-authorization.md`).

## Required behavior
- Canonicalizes the config file's contents via the one system-wide `Canonicalizer` (`jcs_canonicalizer.py`, FR-0.4) before computing/verifying a signature over it — never a second, ad hoc serialization path.
- `verify()` follows the same fail-closed discipline as any other `Verifier` use: an invalid or missing signature results in rejection, not a raised exception the caller must specifically catch to stay safe.

## Inputs / outputs
- **In:** `sign`: raw config bytes. `verify`: config bytes + signature.
- **Out:** `sign`: a signature. `verify`: `bool`.

## Required edge-case behavior (`13-error-and-edge-cases.md`)
- An unsigned `AlgorithmRegistry` config is loaded in a context that requires signing (Recipe B/C) → rejected at load time (`13-error-and-edge-cases.md`).

## Security notes
- **FR-3.3.** The signed-config path is built from the start and is what any non-dev deployment uses; it rejects unsigned config by default.
- **FR-0.4.** Uses `Canonicalizer.canonicalize()` as the only path from config structure to signed bytes — no second serialization path for this file's own config-signing purpose.

## Mandatory tests this must pass
- `tests/test_registry_config_signature.py`
- `tests/security/test_unsigned_config_rejected_when_signing_required.py`

## Non-negotiable principles that apply
- **P1.** Dependency inversion always — constructors take Layer-0 interfaces, never sibling concrete classes.
- **P4.** Mode is a server-side construction fact, never trusted from wire data.

## Explicitly out of scope for this file
- Parsing the YAML structure — `registry_config_loader.py`.
- Deciding when signing is required — `algorithm_registry.py`.

## Source docs
`04-functional-requirements.md`, `09-auth-and-authorization.md`, `10-security-requirements.md`, `13-error-and-edge-cases.md`
