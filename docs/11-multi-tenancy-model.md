# QuantX — Multi-Tenancy Model

**Status:** Pre-implementation, decision-record-style · **Depends on:** D3 (business model), `00-index.md`

## The question this doc answers

The standard SaaS checklist asks: *shared database/shared schema, shared database/separate schema, or separate database per tenant?* For QuantX, the honest answer is **none of these** — and writing that down explicitly (rather than silently skipping it) matters, because it constrains architecture decisions that would otherwise default toward a shared-tenant assumption.

## Why the classic model doesn't apply

Classic SaaS multi-tenancy assumes:

```
User → Organization/Tenant → Resources
```

...with many tenants sharing one running system, isolated at the data layer. QuantX's business model (D3) is **per-client consulting composition**: each client engagement gets its own composed object graph — its own `AlgorithmRegistry` config, its own `KeyValueStore` backend, its own key-custody backend, potentially its own recipe (A/B/C) entirely. There is no single running QuantX instance serving multiple clients at once by design.

| Classic model | Applies to QuantX? |
|---|---|
| Shared DB / shared schema, `tenant_id` column | No — no shared DB exists; `KeyValueStore` has no tenant concept at all |
| Shared DB / separate schema | No — same reason |
| Separate DB per tenant | Closer, but still not quite right — see below |

## What actually provides isolation here

Isolation happens at the **deployment/composition** level, not the data-row level:

- Each client's deployment is its own process (or set of processes) with its own `KeyValueStore` instance (in-memory or its own Redis), its own signed `AlgorithmRegistry` config, and its own key-custody backend.
- There is no cross-client shared infrastructure by default — no shared Redis cluster with tenant-prefixed keys, no shared HSM partition. If a future engagement specifically needs shared infrastructure across a client's own sub-units, that's a decision made *within* that one client's deployment, using their own composition — not a QuantX platform feature.
- A "tenant" in QuantX's world is closer to "a deployment" than "a row in a table." The `subject_id` concept (see `09-auth-and-authorization.md`) is scoped within one deployment's `KeyValueStore`, not globally namespaced.

## What this means for the data model

`07-database-design.md` has no `tenant_id` field anywhere, on purpose. If a specific client engagement genuinely needs sub-tenant isolation *within* their own deployment (e.g. a client with multiple business units), that's modeled as an application-level concern in the `subject_id` scheme, using whatever prefix/namespace convention that client's deployment needs — not as a QuantX platform primitive.

## What this means for the API

`08-api-specification.md` has no `/org/:id/...` routing. Each REST sidecar deployment serves exactly one composed configuration. Multi-client routing, if ever needed, would be an infrastructure decision (separate containers, separate ingress rules) outside QuantX's own code.

## The unit of isolation is a client build (D-011)

Each client receives its own generated source slice and runs its own deployment of it. A hosted-sidecar delivery (`16-delivery-and-factory.md`) is still one deployment per client, so this model holds: no shared state and no shared keys across clients, and one `quantx.yaml` per deployment. Nothing in a client build refers to any other client.

## When to revisit this decision

If the business model itself changes — e.g. QuantX pivots from per-client consulting composition toward a hosted platform serving multiple clients from shared infrastructure — this entire doc needs to be rewritten, along with the data model and API spec, because the isolation guarantees they currently rely on (deployment-level, not row-level) would no longer hold. That's a D3-level business-model change, not a doc update to make lightly or silently.
