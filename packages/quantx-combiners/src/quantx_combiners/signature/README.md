# `signature/` — the signature combiner

## What this is
`SignatureCombiner` and its two isolated concerns: wire framing (`signature_wire_format.py`) and mode enforcement (`signature_mode_enforcement.py`, SR-1). Together, the only signature-combining logic in the system (FR-2.1).

## Part of
`quantx-combiners`, Layer 2. `GATE_REVIEW_REQUIRED` at the package level (`10-security-requirements.md`).

## Contains
- `signature_combiner.py` — the public class, orchestrates only (`GATE_REVIEW_REQUIRED`)
- `signature_wire_format.py` — encode/decode, length-prefixed parsing (not gated — plumbing)
- `signature_mode_enforcement.py` — the `required_mode` cross-check, isolated (SR-1, `GATE_REVIEW_REQUIRED`)

## Why divided this way
Wire parsing, mode enforcement, and orchestration are each isolated so the security-critical logic (mode enforcement) is never mixed into the same file as encoding/decoding plumbing — a reviewer signing off on SR-1 reads one small file, not a combiner that also holds byte-framing details (`14-directory-structure.md`).

## Dependency rules
- `signature_combiner.py` depends on both other files in this folder plus Layer-0 `Verifier`.
- `signature_mode_enforcement.py` depends only on `Mode` — explicitly not on `signature_wire_format.py` (no sideways coupling to the parser).
- `signature_wire_format.py` depends only on Layer-0 types/exceptions — no mode-acceptance logic lives here.

## Independently publishable?
N/A — a subfolder within `quantx-combiners`.

## Source docs
`14-directory-structure.md`, `10-security-requirements.md`, `04-functional-requirements.md`
