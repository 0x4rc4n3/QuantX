"""Push notification authenticator second-factor provider.

Layer: 5
Depends on: quantx_core.interfaces.rate_limiter.RateLimiter, quantx_core.interfaces.replay_store.ReplayStore, quantx_core.interfaces.key_value_store.KeyValueStore, quantx_core.interfaces.clock.Clock, quantx_core.interfaces.canonicalizer.Canonicalizer, quantx_authenticator.push_approval_record.PushApprovalRecord
Implements: PushAuthenticator issuing and verifying push approvals with rate limiting and replay protection
Outside: Network push delivery integration to specific device transports (APNs/FCM)
Inside: Pre-issuance rate limiting (SR-5) and atomic consume-once verification via ReplayStore (SR-11)
Security notes: SR-5 enforces rate limiting prior to send attempt; SR-11 guarantees push approvals cannot be replayed.
"""

from __future__ import annotations

import secrets
from datetime import timedelta
from typing import Any, Callable

from quantx_core.exceptions.rate_limited_error import RateLimitedError
from quantx_core.interfaces.canonicalizer import Canonicalizer
from quantx_core.interfaces.clock import Clock
from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.interfaces.rate_limiter import RateLimiter
from quantx_core.interfaces.replay_store import ReplayStore
from quantx_core.types.ttl import TTL

from quantx_authenticator.push_approval_record import PushApprovalRecord


class PushAuthenticator:
    """Push-based second factor authenticator enforcing SR-5 and SR-11."""

    factor_name: str = "push"

    def __init__(
        self,
        rate_limiter: RateLimiter,
        replay_store: ReplayStore,
        kv_store: KeyValueStore,
        clock: Clock,
        canonicalizer: Canonicalizer,
        ttl_seconds: int = 300,
        send_fn: Callable[[PushApprovalRecord], None] | None = None,
    ) -> None:
        self._rate_limiter = rate_limiter
        self._replay_store = replay_store
        self._kv_store = kv_store
        self._clock = clock
        self._canonicalizer = canonicalizer
        self._ttl_seconds = ttl_seconds
        self._send_fn = send_fn

    def issue(self, subject_id: str) -> PushApprovalRecord:
        """Issue a push approval record. Enforces SR-5 rate limiting prior to sending."""
        # 1. SR-5: Rate limit check MUST happen before sending
        if not self._rate_limiter.allow(subject_id):
            raise RateLimitedError(
                f"Push notification issuance rate limit exceeded for '{subject_id}'"
            )

        now = self._clock.now()
        expires_at = now + timedelta(seconds=self._ttl_seconds)
        approval_id = f"push_{secrets.token_hex(16)}"

        record = PushApprovalRecord(
            approval_id=approval_id,
            subject_id=subject_id,
            issued_at=now,
            expires_at=expires_at,
            consumed=False,
        )

        # 2. Persist in KeyValueStore
        key = f"push:{approval_id}"
        self._kv_store.set(
            key,
            record.to_bytes(self._canonicalizer),
            ttl=TTL(self._ttl_seconds),
        )

        # 3. Trigger external delivery if configured
        if self._send_fn is not None:
            self._send_fn(record)

        return record

    def consume(self, approval_id: str) -> bool:
        """Consume a push approval. Enforces SR-11 single-use replay protection."""
        if not approval_id:
            return False

        key = f"push:{approval_id}"
        raw_bytes = self._kv_store.get(key)
        if raw_bytes is None:
            return False

        try:
            record = PushApprovalRecord.from_json(raw_bytes.decode("utf-8"))
        except Exception:
            return False

        now = self._clock.now()
        if now >= record.expires_at:
            return False

        # SR-11: Atomic single-use consumption through ReplayStore
        ttl_remaining = max(1, int((record.expires_at - now).total_seconds()))
        consumed = self._replay_store.consume_once(
            token=f"push_consumed:{approval_id}",
            ttl=TTL(ttl_remaining),
        )
        if not consumed:
            # Replay detected
            return False

        return True

    def verify_factor(self, subject_id: str, payload: Any) -> bool:
        """Orchestrator second-factor gate interface."""
        if isinstance(payload, str):
            approval_id = payload
        elif isinstance(payload, dict):
            approval_id = str(payload.get("approval_id", ""))
        else:
            return False

        # Validate that the approval matches the subject and can be consumed
        key = f"push:{approval_id}"
        raw = self._kv_store.get(key)
        if raw is None:
            return False
        try:
            record = PushApprovalRecord.from_json(raw.decode("utf-8"))
            if record.subject_id != subject_id:
                return False
        except Exception:
            return False

        return self.consume(approval_id)
