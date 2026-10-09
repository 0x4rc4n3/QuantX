# QuantX: Delivery and the Private Factory

**Status:** Accepted direction (D-011). Licence and contract wording needs a lawyer. **Depends on:** `11-multi-tenancy-model.md`, `15-config-and-composition.md`, `DECISIONS.md` (D-011, D-013).

## The model

The company keeps the full framework and its tooling private. Each client receives only the generated source slice for their own configuration. Clients can read every line they receive, which is intended. What stays private is the factory that decides what goes into a slice and how it is checked.

| Stays private (never delivered) | Delivered to the client |
|---|---|
| Full component set, including options the client did not choose | Packages and files their configuration needs |
| Slicer and generator | Wiring frozen to their choices |
| Builder UI and the full config schema with all options | A narrowed config schema and validator for their options |
| Full test corpus and golden vectors | The tests and vectors for the parts they received |
| Release and patch pipeline, review process | Lockfile, SBOM, build manifest, licence and notice files |

## What the factory contains

`factory/` is a separate private directory at the repository root. It is not a package, is never published, and is excluded from every slice.

```
factory/
├── slicer/        # config -> dependency closure -> file list
├── generator/     # writes frozen wiring, narrowed schema, manifest
├── builder/       # quantx-builder.html (puzzle configurator) and quantx-puzzle.html
├── release/       # lockfile, SBOM, image build and signing, patch rebuilds
└── tests/         # slice-leak tests, reproducibility tests, manifest tests
```

File-level specs for `factory/` follow the same one-file-one-job convention and are written when the factory is started (build order step 12). This document is the contract until then.

## Slicer rules

- **SLICE-1.** Input is a validated `quantx.yaml` (`15`). Output is the minimum set of packages and files for that config, found by static dependency closure from the chosen components.
- **SLICE-2.** Unchosen adapters, backends and options are absent: no file, no import, no registry entry, no mention in comments or docs.
- **SLICE-3.** Generated wiring has the choices frozen in. The delivered tree has no menu of other options.
- **SLICE-4.** The delivered config schema accepts only the options in the slice.
- **SLICE-5.** Output is reproducible: the same config and framework version give byte-identical output apart from the build ID stamp.
- **SLICE-6.** Generated output is never edited by hand. A client-specific change goes into the private repo and is rebuilt.
- **SLICE-7.** Leak test: for each recipe, assert that excluded file names and identifiers do not appear anywhere in the output.

## Build manifest

Every delivered build includes a manifest: client ID, build ID, framework version and commit, SHA-256 of the config, dependency lockfile hash, SBOM reference, test results, and a review status for each `gated` component. Review status is `unreviewed` unless a sign-off record from someone other than the author is attached (P7, SR-6, SR-15). A build is never described as reviewed, audited or production-ready without that record.

## Delivery options

| Option | When | Notes |
|---|---|---|
| Source slice (default) | Most clients | Client owns and audits the code. The most transparent. |
| Hosted sidecar | Clients who want no operations burden | The company runs the image (D-013). Each client is still its own deployment, so `11` holds. |
| Source escrow | Clients who need continuity | A neutral agent holds the source slice and the build instructions, released on defined events. |

Compiled wheels and obfuscation are not used: weak protection and harder for a client to audit.

## Maintenance

A CVE in pyca or OpenSSL, or a fix in a component, triggers an automatic rebuild of every affected client slice from the private repo. Each rebuild gets release notes and a new manifest. Support and patch obligations (response times, supported versions, end of life) go in the client contract.

## Protecting the business (checklist for the lawyer)

This is a checklist, not legal advice. Jurisdiction matters, and enforcing across borders is hard.

1. **Licence on delivered code.** Use for the client's own systems only; no redistribution or sublicensing; no use to build or offer a competing product or service; client may modify its own slice but not merge it into other products.
2. **NDA** covering the factory, the config format, the builder and any tooling the client sees.
3. **Confidentiality of non-delivered parts** and a ban on reverse engineering the factory.
4. **Term and termination**, including what happens to the code and any escrow.
5. **Escrow** release conditions, if offered.
6. **Warranty disclaimer, liability cap, and a vulnerability disclosure process.**
7. **Export controls.** Cryptographic software can be regulated for export; check the rules in the company's country and each client's.
8. **Third-party licences**, from the SBOM, checked for conflicts with the client licence.
9. **Ownership** of client-specific customizations.
10. **Trademark** on the QuantX name: check availability, then register. Control how clients may use the name.
11. **Build ID watermark** with the client's consent, so a leaked copy can be traced.
12. **Trade-secret handling of the factory:** private repo, short access list, MFA, no secrets or factory code in public CI logs, offboarding steps for people who leave.

## What this does not protect

The idea and the business model are not protectable. A competitor can read a delivered component and reimplement it. The lasting edge is the factory, the quality and independence of the review, speed of delivery, and maintenance.
