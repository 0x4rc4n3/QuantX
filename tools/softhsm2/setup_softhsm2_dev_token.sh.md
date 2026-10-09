# `setup_softhsm2_dev_token.sh`

**Location:** `tools/softhsm2/` · **Status:** pre-implementation — this is the spec for a file that does not exist yet.

## Purpose
Installs SoftHSM2 and provisions a dev PKCS#11 token/slot, so `hsm_pkcs11_backend.py` gets built and tested against a real HSM-class interface from the start — `02-build-order.md`'s named resolution to the real blocker "HSM integration needs physical/cloud HSM access": "Don't wait for client-specific hardware — install SoftHSM2 ... immediately and build/test the PKCS#11 integration for real."

## Required contents / behavior
- Installs the SoftHSM2 package for the current dev/CI environment.
- Initializes a token/slot with a known PIN, suitable for `hsm_pkcs11_backend.py`'s test suite to use.
- Idempotent — safe to re-run without duplicating tokens `(inferred: standard practice for a setup script; not explicitly required by the docs)`.

## Non-negotiable principles that apply
- **P7.** Nothing is called "production-ready", "audited", or "reviewed" until it actually has been, by someone other than the author.

## Source docs
`02-build-order.md`
