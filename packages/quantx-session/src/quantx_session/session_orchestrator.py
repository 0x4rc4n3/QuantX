"""
Layer: 4
Depends on: SignatureCombiner/KEMCombiner (Layer 2), ReplayStore, RateLimiter, Clock, KeyValueStore (Layer 0); optionally TotpProvider/PushAuthenticator (Layer 5) as additional configured gates
Implements: finish(challenge_id, signed_response) -> SessionToken; validate(token) -> bool
Outside: The actual cryptographic verification logic — delegates entirely to SignatureCombiner/KEMCombiner; TOTP/push verification logic itself — delegates to Layer 5.
Inside: Gate sequencing: primary factor -> configured second factors -> replay check -> rate limit -> token minting, in that order, with no early token creation.
Security notes: SR-10 in full: token minted only as the final statement after every required gate passes.
"""

from __future__ import annotations

import secrets
from datetime import timedelta
from typing import Any, Mapping, Sequence

from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.exceptions.rate_limited_error import RateLimitedError
from quantx_core.exceptions.replay_detected_error import ReplayDetectedError
from quantx_core.interfaces.clock import Clock
from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.interfaces.rate_limiter import RateLimiter
from quantx_core.interfaces.replay_store import ReplayStore
from quantx_core.interfaces.verifier import Verifier
from quantx_core.types.ttl import TTL

from quantx_session.challenge_record import ChallengeRecord
from quantx_session.session_token import SessionToken


class SessionOrchestrator:
    """
    SessionOrchestrator enforces gating across primary factor, optional second factors,
    replay protection, dual rate limiting, and mint-last session token creation (SR-10).
    """

    def __init__(
        self,
        kv_store: KeyValueStore,
        replay_store: ReplayStore,
        identity_rate_limiter: RateLimiter,
        global_rate_limiter: RateLimiter,
        clock: Clock,
        combiners_by_role: Mapping[str, Verifier],
        session_ttl_seconds: int = 3600,
        second_factor_gates: Sequence[Any] | None = None,
    ) -> None:
        self._kv_store = kv_store
        self._replay_store = replay_store
        self._identity_rate_limiter = identity_rate_limiter
        self._global_rate_limiter = global_rate_limiter
        self._clock = clock
        self._combiners_by_role = dict(combiners_by_role)
        self._session_ttl_seconds = session_ttl_seconds
        self._second_factor_gates = list(second_factor_gates or [])

    def start(
        self,
        challenge_id: str,
        identity_key: str,
    ) -> None:
        """
        Validate rate limit and initial prerequisites prior to submission.
        """
        if not self._global_rate_limiter.allow("global"):
            raise RateLimitedError("Global rate limit exceeded")
        if not self._identity_rate_limiter.allow(identity_key):
            raise RateLimitedError(f"Identity rate limit exceeded for '{identity_key}'")

    def finish(
        self,
        challenge_id: str,
        signed_response: bytes,
        second_factor_payloads: Mapping[str, Any] | None = None,
    ) -> SessionToken:
        """
        Finish session authentication flow. Enforces gates strictly in sequence:
        1. Fetch challenge record from KeyValueStore. Check expiration.
        2. Replay check (consume challenge_id exactly once via ReplayStore).
        3. Rate limiter check (global and per-identity).
        4. Primary-factor cryptographic verification via role SignatureCombiner.
        5. Any configured second-factor verification gates.
        6. MINT LAST: construct and store SessionToken only after all above succeed (SR-10).
        """
        # 1. Fetch challenge
        chal_key = f"challenge:{challenge_id}"
        chal_bytes = self._kv_store.get(chal_key)
        if chal_bytes is None:
            raise MalformedInputError(f"Challenge '{challenge_id}' not found or expired")

        try:
            record = ChallengeRecord.from_json(chal_bytes.decode("utf-8"))
        except Exception as exc:
            raise MalformedInputError(f"Malformed challenge record in store: {exc}") from exc

        now = self._clock.now()
        if now >= record.expires_at:
            raise MalformedInputError(f"Challenge '{challenge_id}' has expired")

        # 2. Replay check (consume challenge_id exactly once)
        ttl_remaining = max(1, int((record.expires_at - now).total_seconds()))
        consumed = self._replay_store.consume_once(
            f"chal_consumed:{challenge_id}", TTL(ttl_remaining)
        )
        if not consumed:
            raise ReplayDetectedError(
                f"Challenge '{challenge_id}' has already been consumed (replay detected)"
            )

        # 3. Rate limiter check
        if not self._global_rate_limiter.allow("global"):
            raise RateLimitedError("Global rate limit exceeded")
        if not self._identity_rate_limiter.allow(record.subject_id):
            raise RateLimitedError(f"Identity rate limit exceeded for '{record.subject_id}'")

        # 4. Primary-factor verification
        if record.role_id not in self._combiners_by_role:
            raise MalformedInputError(f"Role '{record.role_id}' not configured on orchestrator")

        combiner = self._combiners_by_role[record.role_id]
        # Verify over canonical nonce
        if not combiner.verify(signed_response, record.nonce):
            raise MalformedInputError("Primary factor signature verification failed")

        factors_completed: list[str] = ["primary"]

        # 5. Optional second-factor gates (Layer 5)
        if self._second_factor_gates:
            payloads = second_factor_payloads or {}
            for gate in self._second_factor_gates:
                # Each gate must implement verify_factor(subject_id, payload) -> bool
                factor_name = getattr(gate, "factor_name", "second_factor")
                payload = payloads.get(factor_name)
                if not gate.verify_factor(record.subject_id, payload):
                    raise MalformedInputError(f"Second factor '{factor_name}' verification failed")
                factors_completed.append(factor_name)

        # 6. MINT LAST: only reached if every prior gate passed (SR-10)
        token_id = f"tok_{secrets.token_hex(24)}"
        expires_at = now + timedelta(seconds=self._session_ttl_seconds)

        token = SessionToken(
            token_id=token_id,
            subject_id=record.subject_id,
            issued_at=now,
            expires_at=expires_at,
            factors_completed=tuple(factors_completed),
        )

        # Persist session token in KeyValueStore
        token_key = f"session:{token_id}"
        self._kv_store.set(
            token_key,
            token.to_bytes(),
            ttl=TTL(self._session_ttl_seconds),
        )

        # Clean up challenge key
        self._kv_store.delete(chal_key)

        return token

    def validate(self, token_or_id: SessionToken | str) -> bool:
        """
        Validate whether a session token is active and unexpired.
        """
        token_id = token_or_id.token_id if isinstance(token_or_id, SessionToken) else token_or_id
        token_key = f"session:{token_id}"
        raw_bytes = self._kv_store.get(token_key)
        if raw_bytes is None:
            return False

        try:
            token = SessionToken.from_json(raw_bytes.decode("utf-8"))
            now = self._clock.now()
            return now < token.expires_at
        except Exception:
            return False
