"""
Layer: 4
Depends on: KeyValueStore, Clock, Canonicalizer (Layer 0); ChallengeRecord (this package)
Implements: issue(subject_id: str, role_id: str = "session-auth", ttl_seconds: int = 300) -> ChallengeRecord
Outside: Verifying the signed response — SessionOrchestrator's job.
Inside: Constructing a ChallengeRecord (nonce, issued_at/expires_at via Clock, required_mode set server-side) and persisting it through KeyValueStore.
Security notes: FR-4.1: stored via KeyValueStore, never held in process memory outside that interface. required_mode set here is never later overridden by anything wire-derived (SR-1). Nonce canonicalized via Canonicalizer (FR-0.4).
"""

from __future__ import annotations

import secrets
from datetime import timedelta
from typing import Mapping

from quantx_core.interfaces.canonicalizer import Canonicalizer
from quantx_core.interfaces.clock import Clock
from quantx_core.interfaces.key_value_store import KeyValueStore
from quantx_core.types.mode import Mode
from quantx_core.types.ttl import TTL

from quantx_session.challenge_record import ChallengeRecord


class ChallengeIssuer:
    """
    Issues single-use cryptographic challenges and stores them via KeyValueStore (FR-4.1).
    """

    def __init__(
        self,
        kv_store: KeyValueStore,
        clock: Clock,
        canonicalizer: Canonicalizer,
        role_modes: Mapping[str, Mode],
    ) -> None:
        self._kv_store = kv_store
        self._clock = clock
        self._canonicalizer = canonicalizer
        self._role_modes = dict(role_modes)

    def issue(
        self,
        subject_id: str,
        role_id: str = "session-auth",
        ttl_seconds: int = 300,
    ) -> ChallengeRecord:
        """
        Issue an authentication challenge for a subject and role.
        """
        if not subject_id:
            raise ValueError("subject_id must be non-empty")
        if role_id not in self._role_modes:
            raise ValueError(f"Unknown registry role for challenge issuance: '{role_id}'")

        required_mode = self._role_modes[role_id]
        now = self._clock.now()
        expires_at = now + timedelta(seconds=ttl_seconds)

        # Generate random 32-byte nonce
        raw_nonce = secrets.token_bytes(32)

        # Canonicalize nonce data structure via Canonicalizer (FR-0.4)
        nonce_dict = {
            "type": "challenge_nonce",
            "subject_id": subject_id,
            "role_id": role_id,
            "raw_nonce_hex": raw_nonce.hex(),
            "issued_at": now.isoformat(),
        }
        canonical_nonce = self._canonicalizer.canonicalize(nonce_dict)

        challenge_id = f"chal_{secrets.token_hex(16)}"

        record = ChallengeRecord(
            challenge_id=challenge_id,
            subject_id=subject_id,
            role_id=role_id,
            nonce=canonical_nonce,
            issued_at=now,
            expires_at=expires_at,
            required_mode=required_mode,
        )

        # Store in KeyValueStore with TTL
        key = f"challenge:{challenge_id}"
        record_bytes = record.to_bytes(self._canonicalizer)
        self._kv_store.set(key, record_bytes, ttl=TTL(ttl_seconds))

        return record
