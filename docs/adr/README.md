# `adr/` — architecture decision records for gated components

## What this is
One file per `GATE_REVIEW_REQUIRED` component group (`10-security-requirements.md`'s review-gates list) — where the eventual outside-reviewer sign-off gets logged before any of those components may be called "production-ready" (`BUILD_PROMPT.md` §5).

## Part of
`docs/`.

## Contains
- `signature_combiner.md` — `SignatureCombiner`, `signature_mode_enforcement.py` (SR-1)
- `kem_combiner.md` — `KEMCombiner`, `kem_hkdf_binding.py` (SR-7)
- `algorithm_registry.md` — `AlgorithmRegistry` (FR-3.1)
- `key_wallet_backends.md` — `EncryptedFileBackend` (SR-9), `OSKeychainBackend`/`HsmPkcs11Backend` (SR-6)
- `threshold_policy_and_manager.md` — `ThresholdPolicy` (SR-12), `ThresholdManager`
- `merkle_and_anonymous_proof.md` — `MerkleMembershipProof` (SR-2), `AnonymousProofBackend`

## Why divided this way
One ADR per component *group* (not per individual file) mirrors `BUILD_PROMPT.md` §5's gate-review notice text, which names a single ADR file per group of related gated components (e.g. both signature-side gated files point at `signature_combiner.md`).

## Dependency rules
- Each gated `.py.md` spec file's `GATE_REVIEW_REQUIRED` notice names exactly one of these six files as where its sign-off must be logged — until that sign-off is logged, per `BUILD_PROMPT.md` §5, that component may not be called production-ready in any doc, README, or client material.

## Source docs
`10-security-requirements.md`
