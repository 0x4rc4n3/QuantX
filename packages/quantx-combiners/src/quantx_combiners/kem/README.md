# `kem/` — the KEM combiner

## What this is
`KEMCombiner` and its two isolated concerns: wire framing (`kem_wire_format.py`) and HKDF ciphertext/public-key binding (`kem_hkdf_binding.py`, SR-7). Together, the only KEM-combining logic in the system (FR-2.2).

## Part of
`quantx-combiners`, Layer 2. `GATE_REVIEW_REQUIRED` at the package level.

## Contains
- `kem_combiner.py` — the public class, orchestrates only (`GATE_REVIEW_REQUIRED`)
- `kem_wire_format.py` — encode/decode (not gated — plumbing)
- `kem_hkdf_binding.py` — ciphertext/public-key → HKDF `info` binding (SR-7, `GATE_REVIEW_REQUIRED`)

## Why divided this way
Same rationale as `signature/` — the security-critical binding logic is isolated from encoding/decoding plumbing so a reviewer signing off on SR-7 reads one small file.

## Dependency rules
- `kem_combiner.py` depends on both other files plus Layer-0 `KEMProvider`.
- `kem_hkdf_binding.py` depends only on `cryptography`'s HKDF — explicitly not on `kem_wire_format.py`.
- `kem_wire_format.py` depends only on Layer-0 types/exceptions.

## Independently publishable?
N/A — a subfolder within `quantx-combiners`.

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`, `04-functional-requirements.md`
