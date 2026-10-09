# QuantX — Build Order

**Status:** Pre-implementation · **Replaces:** any earlier phase/roadmap framing. There are no phases. There is one build order, driven entirely by dependency structure, and every component in it gets built to the same bar of quality — nothing is scoped down to "minimum viable," and nothing is deferred pending a client asking for it.

## The rule

Build strictly in dependency order: a layer is started only once every layer it depends on is done and tested. Within that constraint, move as fast as the work allows — there's no artificial pacing, no "wait for Phase N to be declared complete" gate between layers. The only things that legitimately don't ship immediately are the two cases in **Real (non-arbitrary) blockers** below — both are gated by an actual external dependency, not by schedule.

## Build order

**0 — Foundational interfaces.** `Signer`, `Verifier`, `KEMProvider`, `Canonicalizer`, `Clock`, `KeyValueStore`, `ReplayStore`, `RateLimiter`, plus `InMemoryKVStore` and `JCSCanonicalizer` as reference implementations. Nothing above this layer can be meaningfully built or tested first. Done when every interface has a `Protocol` definition and `InMemoryKVStore`/`JCSCanonicalizer` pass their own unit tests, including the hard `max_entries` cap behavior.

**1 — Algorithm adapters.** Seven of the eight, together, in one pass (D10): Ed25519, ECDSA-P256, ML-DSA-65, ML-DSA-87, X25519, ML-KEM-768, ML-KEM-1024. SLH-DSA is specified but upstream-blocked (`cryptography` has no SLH-DSA yet; D-006): it is built the moment pyca ships it, with no substitute library. Each is a small, uniform file — there's no reason to build some now and leave the rest for later. Done when every adapter round-trips `generate_keypair → sign/encapsulate → verify/decapsulate` correctly and `verify()`/`decapsulate()` fail closed on malformed input.

**2 — Combiners.** `SignatureCombiner`, `KEMCombiner` — exactly one of each, ever. This is the layer that carries the most weight (mode enforcement, KEM ciphertext/key binding), so it gets the most test attention before moving on: the downgrade test, the ciphertext/public-key substitution test, and — new here — fuzz/property-based tests on the wire-format parser (`_parse`) using malformed and adversarially-sized length fields, not just the deterministic regression cases. Done when both combiners pass all of that and are queued for outside review (`10-security-requirements.md`).

**3 — Algorithm registry.** `AlgorithmRegistry`, YAML-loaded, signature-verifiable. Build the signed-config path now, not later — don't ship an "unsigned for now, signed eventually" version. `allow_unsigned=True` still exists as an explicit, opt-in dev/test convenience, but the signed path is real from day one. Done when it resolves every registry role to a correctly-wired combiner and rejects unsigned/invalid-signature config by default.

**4 — Session primitives.** `ChallengeIssuer`, `SessionOrchestrator`. This is where the whole system becomes demonstrable end-to-end: `default_setup()` → `start()` → `finish()` → `validate()`. Done when that full flow works, every mandatory security test in `10-security-requirements.md` passes against it, and Layers 0–2 have cleared outside review. This is the first point where there's something worth showing someone outside the build.

**5 — Second factor (verification logic).** `TotpProvider`, `PushAuthenticator`. Build the verification/rate-limiting logic and wire both into `SessionOrchestrator` as additional gates now. Per D11, hold off only on *durable* TOTP secret storage — build against test-fixture secrets until Layer 6 exists, then come back and wire the real store through in the same pass Layer 6 lands (see the note under Layer 6). Done when both factors gate the orchestrator correctly and each has its own independent rate limiter and replay protection.

**6 — Key custody.** `KeyWallet`, `EncryptedFileBackend`, `OSKeychainBackend`, `HsmPkcs11Backend`. Build all three backends now, not just the file-based one — see **Real blockers** below for how to unblock the HSM backend immediately rather than waiting on client hardware. The moment this layer is done, go back and complete Layer 5: wire `TotpProvider`'s secret storage through `KeyWallet`, replacing the test-fixture secrets. Done when vault metadata is AAD-authenticated, corruption raises rather than returning empty, and every backend either really works or raises `BackendUnavailableError`/`NotImplementedError` — never a silent fallback.

**7 — Recovery.** `BackupCodeManager`, `DeviceLinker`. Straightforward once Layer 6 exists. Done when backup codes are single-use-verified and device-pairing tokens can't be replayed.

**8 — Governance.** `ThresholdPolicy`, `ThresholdManager`. Built now, not held back for a specific client's board-approval use case — the components are generically useful the moment `SignatureCombiner` exists, and there's no reason to leave working code on the shelf. Done when duplicate-key rejection is enforced at policy creation and `finalize()` correctly composes on top of the existing `SignatureCombiner`, no reimplemented verification logic.

**9 — Membership proofs.** `MerkleMembershipProof` ships now, fully built and reviewed. `AnonymousProofBackend` stays an interface only — see **Real blockers** below; this is not a scheduling deferral, it's a hard rule. Done (for the Merkle component) when `verify_proof()` actually walks the path to the root and the non-anonymity caveat is stated everywhere the component is surfaced.

**10 — Observability & compliance.** `CryptoBOMModel`, `StaticSourceScanner`, `TlsInspector`, `StandardsCatalog`, `ComplianceReportGenerator`. This layer has no dependency on Layers 1–9 at all — it's a standalone tool. It's sequenced last here only because this is a single linear build order; if a second contributor is ever available, this is the layer to hand off in parallel rather than waiting. Done when the scanner's disclaimer ships with every report, not just its README, and `TlsInspector` tags every finding by trust level.

**11 — Configuration and CLI.** `config.py` (schema, loader, validator), `cli.py`, and the narrowing of `wiring.py` to read `quantx.yaml` (`15-config-and-composition.md`, D-012). The first version lands with Layer 4 and the sidecar so Recipe A runs from a file; it is finished when every option that reached `available` status (D-014) has validator rules and a fixture. Done when Recipes A, B and C each pass an end-to-end test from their example file, and every error rule has a failing fixture.

**12 — Factory (private).** Conformance suites per Layer 0 interface, the slicer, generator, builder export and release pipeline (`16-delivery-and-factory.md`, D-011). It depends on 11 and on the tests of every layer a slice can include. Done when each recipe produces a reproducible slice that passes its own tests and the slice-leak test, with a build manifest. `factory/` is never packaged or delivered.

## Packaging isn't a final step — it surfaces as you go

The REST sidecar depends only on Layer 4. Stand it up as soon as Layer 4 is done, so there's an installable, demoable artifact early — then extend its surface as Layers 5–10 land, rather than holding packaging back until the whole stack is finished. See `08-api-specification.md` for the contract.

## Real (non-arbitrary) blockers — the only two exceptions to "build it now"

- **`HsmPkcs11Backend`** needs an actual PKCS#11 module to build and test against. Don't wait for client-specific hardware — install **SoftHSM2** (a software PKCS#11 implementation) immediately as the development/test target, so this backend gets built for real, on the same timeline as everything else. Swapping in a client's real HSM later is then a configuration change, not new code.
- **`AnonymousProofBackend`** has no reference implementation on purpose. A real anonymous-membership scheme needs a vetted circuit library or an independently audited from-scratch construction — building an unaudited approximation is the exact mistake this interface exists to prevent. This gate is about audit availability, not calendar time: the moment a specific vetted implementation and a qualified reviewer are lined up, it can be built and reviewed regardless of where the rest of the build order stands.

## Definition of done (applies to every layer above)

- Unit tests pass, including any mandatory security test from `10-security-requirements.md` that applies.
- Docstring states Layer, Depends on, Implements, Outside, Inside, Wire format (if any), Security notes.
- No import of a sibling concrete class above Layer 1, except `AlgorithmRegistry`.
- Lint/format/type-check all pass, no exceptions merged.
- If flagged for outside review in `10-security-requirements.md`: review actually completed and logged before anything calls it production-ready.
