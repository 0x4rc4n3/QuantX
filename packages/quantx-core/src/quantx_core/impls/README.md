# `impls/` — Layer-0 reference implementations

## What this is
The concrete, dev-grade and production-grade implementations of the Layer-0 interfaces — what actually gets wired into `default_setup()` (Recipe A) or a real deployment (Recipe B).

## Part of
`quantx-core`, Layer 0.

## Contains
- `in_memory_kv_store.py` — `KeyValueStore`, dev/test only, hard `max_entries` cap (SR-3)
- `redis_kv_store.py` — `KeyValueStore`, networked, optional `redis` extra (SR-4)
- `jcs_canonicalizer.py` — `Canonicalizer`, RFC 8785, the one canonicalization path (SR-8)
- `system_clock.py` — `Clock`, the one place wall-clock time is read (SR-14)
- `in_memory_replay_store.py` — `ReplayStore`, consume-once semantics (SR-11)
- `in_memory_rate_limiter.py` — `RateLimiter`, backs every independent limiter instance

## Why divided this way
One implementation per file per `14-directory-structure.md`'s atomicity rule — `redis_kv_store.py` in particular is split from `in_memory_kv_store.py` so the optional `redis` dependency doesn't leak into every Recipe-A consumer.

## Dependency rules
- Each file depends on exactly the one `interfaces/` Protocol it implements, plus (per P5/FR-0.2) `key_value_store.py` where a stateful impl needs backing storage of its own.
- Never imports a sibling concrete class in this folder (P1).

## Source docs
`06-system-architecture.md`, `10-security-requirements.md`, `07-database-design.md`
