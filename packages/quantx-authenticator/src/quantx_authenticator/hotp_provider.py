"""HMAC-based One-Time Password (HOTP) provider.

Layer: 5
Depends on: quantx_core.interfaces.rate_limiter.RateLimiter, quantx_core.interfaces.key_value_store.KeyValueStore
Implements: HotpProvider verifying counter-based OTP codes per RFC 4226 and D-015
Outside: Time-based verification (TotpProvider) and durable KeyWallet hardware custody
Inside: Look-ahead counter search window (10), successful verification counter advancement, and independent rate limiting
Security notes: Independent rate limiter prevents brute-force search; counter advances only after successful verification (D-015).
"""

from __future__ import annotations

import hmac
from typing import Any, Mapping

from quantx_core.exceptions.rate_limited_error import RateLimitedError
from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.interfaces.rate_limiter import RateLimiter

from quantx_authenticator.totp_provider import compute_hotp_code


class HotpProvider:
    """HOTP second-factor provider implementing RFC 4226 and D-015."""

    factor_name: str = "hotp"

    def __init__(
        self,
        rate_limiter: RateLimiter,
        kv_store: KeyValueStore,
        lookahead_window: int = 10,
        digits: int = 6,
        secrets: Mapping[str, bytes] | None = None,
    ) -> None:
        self._rate_limiter = rate_limiter
        self._kv_store = kv_store
        self._lookahead_window = lookahead_window
        self._digits = digits
        self._secrets: dict[str, bytes] = dict(secrets or {})

    def register_secret(self, subject_id: str, secret: bytes, initial_counter: int = 0) -> None:
        """Register or update test-fixture secret and initial counter for a subject."""
        self._secrets[subject_id] = secret
        self.set_counter(subject_id, initial_counter)

    def get_counter(self, subject_id: str) -> int:
        """Fetch current counter value for a subject from KeyValueStore."""
        key = f"hotp_counter:{subject_id}"
        val = self._kv_store.get(key)
        if val is None:
            return 0
        try:
            return int(val.decode("ascii"))
        except Exception:
            return 0

    def set_counter(self, subject_id: str, counter: int) -> None:
        """Persist updated counter value for a subject."""
        key = f"hotp_counter:{subject_id}"
        self._kv_store.set(key, str(counter).encode("ascii"))

    def generate_code(self, subject_id: str, counter_override: int | None = None) -> str:
        """Generate HOTP code for subject at current or specified counter."""
        secret = self._secrets.get(subject_id)
        if not secret:
            raise ValueError(f"No secret registered for subject '{subject_id}'")
        cnt = counter_override if counter_override is not None else self.get_counter(subject_id)
        return compute_hotp_code(secret=secret, counter=cnt, digits=self._digits)

    def verify(self, subject_id: str, code: str) -> bool:
        """Verify HOTP code against lookahead window and increment counter on success (D-015)."""
        # 1. Independent rate-limiting check
        if not self._rate_limiter.allow(subject_id):
            raise RateLimitedError(f"HOTP verification rate limit exceeded for '{subject_id}'")

        secret = self._secrets.get(subject_id)
        if not secret:
            return False

        cleaned_code = code.strip()
        if len(cleaned_code) != self._digits or not cleaned_code.isdigit():
            return False

        current_counter = self.get_counter(subject_id)

        # 2. Search look-ahead window
        for offset in range(self._lookahead_window):
            test_counter = current_counter + offset
            expected = compute_hotp_code(secret=secret, counter=test_counter, digits=self._digits)
            if hmac.compare_digest(cleaned_code, expected):
                # Successful match: advance counter past the matched value
                self.set_counter(subject_id, test_counter + 1)
                return True

        # Failed verification: counter does not advance
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
