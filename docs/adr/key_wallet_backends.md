# `key_wallet_backends.md`

**Location:** `docs/adr/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
The architecture decision record where the three `KeyWallet` custody backends's eventual outside-reviewer sign-off gets logged, per `BUILD_PROMPT.md` §5's `GATE_REVIEW_REQUIRED` notice.

## Required contents / behavior
- **Components covered:** `packages/quantx-wallet/src/quantx_wallet/backends/encrypted_file_backend.py` (SR-9), `.../os_keychain_backend.py` (SR-6), `.../hsm_pkcs11_backend.py` (SR-6)
- **Status at doc-generation time: UNREVIEWED.** No sign-off has been logged — none of the components above may be called "production-ready" in any doc, README, or client material until someone *other than the implementing author* has reviewed the eventual implementation and logged that review here.
- **What the reviewer should confirm:** That each backend either genuinely works against its real target (file/AEAD, OS keychain, PKCS#11/HSM) or raises an explicit typed error — never a silent fallback to weaker behavior — and that vault metadata is authenticated inside the AEAD AAD.
- **Sign-off log:** *(empty — to be filled in in a future pass, once implementation and outside review actually happen. An AI coding agent completing the components above is the author for gate-review purposes, and may not sign off on its own work here.)*

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Source docs
`10-security-requirements.md`, `14-directory-structure.md`

## Addendum (2026-10-04, D-008)

Production custody is resident-key: `hsm_pkcs11`, `aws_kms`, `gcp_kms`. Software backends (`encrypted_file`, `os_keychain`, in-memory) are dev and staging only. Resident-key backends add `generate`, `signer_for` and `decapsulator_for`, and `retrieve` raises `KeyNotExportableError`. Vault is a source of secret references only.
