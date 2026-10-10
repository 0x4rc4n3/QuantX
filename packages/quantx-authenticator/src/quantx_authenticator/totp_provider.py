"""Time-based One-Time Password (TOTP) provider.

Layer: 5
Depends on: quantx_core.interfaces.rate_limiter.RateLimiter, quantx_core.interfaces.clock.Clock, quantx_core.interfaces.replay_store.ReplayStore, quantx_core.types.ttl.TTL
Implements: TotpProvider verifying time-based OTP codes per RFC 6238 and D-015
Outside: Primary-factor verification and long-term hardware custody
Inside: HMAC-SHA1 code derivation, +/- 1 drift window verification, single-use step consumption, and independent rate limiting
Security notes: FR-5.2 independent rate limiter protects against brute-force attacks; D-015 step consumption prevents token reuse.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any, Mapping

from quantx_core.exceptions.rate_limited_error import RateLimitedError
from quantx_core.interfaces.clock import Clock
from quantx_core.interfaces.rate_limiter import RateLimiter
from quantx_core.interfaces.replay_store import ReplayStore
from quantx_core.types.ttl import TTL


def compute_hotp_code(secret: bytes, counter: int, digits: int = 6) -> str:
    """Compute HOTP code for a secret and 64-bit integer counter per RFC 4226."""
    counter_bytes = counter.to_bytes(8, byteorder="big")
    digest = hmac.new(secret, counter_bytes, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary_code = (
        ((digest[offset] & 0x7F) << 24)
        | ((digest[offset + 1] & 0xFF) << 16)
        | ((digest[offset + 2] & 0xFF) << 8)
        | (digest[offset + 3] & 0xFF)
    )
    otp = binary_code % (10**digits)
    return f"{otp:0{digits}d}"


class TotpProvider:
    """TOTP second-factor provider implementing RFC 6238 and D-015."""

    factor_name: str = "totp"

    def __init__(
        self,
        rate_limiter: RateLimiter,
        clock: Clock,
        replay_store: ReplayStore,
        step_seconds: int = 30,
        digits: int = 6,
        allowed_drift_steps: int = 1,
        secrets: Mapping[str, bytes] | None = None,
        wallet: Any | None = None,
    ) -> None:
        self._rate_limiter = rate_limiter
        self._clock = clock
        self._replay_store = replay_store
        self._step_seconds = step_seconds
        self._digits = digits
        self._allowed_drift_steps = allowed_drift_steps
        self._secrets: dict[str, bytes] = dict(secrets or {})
        self._wallet = wallet

    def _get_secret(self, subject_id: str) -> bytes | None:
        if self._wallet is not None:
            retrieved = self._wallet.retrieve(subject_id)
            if isinstance(retrieved, bytes):
                return retrieved
        return self._secrets.get(subject_id)

    def register_secret(self, subject_id: str, secret: bytes) -> None:
        """Register or update secret for a subject in KeyWallet or memory (D11)."""
        if self._wallet is not None:
            self._wallet.store(subject_id, secret)
        self._secrets[subject_id] = secret

    def generate_code_for_step(self, secret: bytes, step: int) -> str:
        """Generate formatted TOTP code for a specific time step counter."""
        return compute_hotp_code(secret=secret, counter=step, digits=self._digits)

    def generate_code(self, subject_id: str, offset_seconds: int = 0) -> str:
        """Generate current TOTP code for a subject given current clock time."""
        secret = self._get_secret(subject_id)
        if not secret:
            raise ValueError(f"No secret registered for subject '{subject_id}'")
        now_ts = self._clock.now().timestamp() + offset_seconds
        step = int(now_ts // self._step_seconds)
        return self.generate_code_for_step(secret=secret, step=step)

    def verify(self, subject_id: str, code: str) -> bool:
        """Verify TOTP code for a subject.

        Enforces independent rate limiting (FR-5.2), checks time drift (+/- 1 step),
        and consumes accepted time step through ReplayStore (D-015).
        """
        # 1. Independent rate-limiting check
        if not self._rate_limiter.allow(subject_id):
            raise RateLimitedError(f"TOTP verification rate limit exceeded for '{subject_id}'")

        secret = self._get_secret(subject_id)
        if not secret:
            return False

        cleaned_code = code.strip()
        if len(cleaned_code) != self._digits or not cleaned_code.isdigit():
            return False

        now_ts = self._clock.now().timestamp()
        current_step = int(now_ts // self._step_seconds)

        # 2. Check current and adjacent drift steps
        for drift in range(-self._allowed_drift_steps, self._allowed_drift_steps + 1):
            target_step = current_step + drift
            expected = self.generate_code_for_step(secret=secret, step=target_step)
            if hmac.compare_digest(cleaned_code, expected):
                # 3. Single-use consumption per D-015
                consumed = self._replay_store.consume_once(
                    token=f"totp_step:{subject_id}:{target_step}",
                    ttl=TTL(self._step_seconds * 3),
                )
                if not consumed:
                    # Replay detected for this step window
                    return False
                return True

        return False

    def verify_factor(self, subject_id: str, payload: Any) -> bool:
        """Orchestrator second-factor gate interface."""
        if isinstance(payload, str):
            code = payload
        elif isinstance(payload, dict):
            code = str(payload.get("code", ""))
        else:
            return False
        return self.verify(subject_id=subject_id, code=code)
