"""End-to-end security test for SR-6: Custody backend unavailability raises explicit error.

Layer: cross-cutting
Depends on: quantx_wallet.key_wallet.KeyWallet, quantx_authenticator.totp_provider.TotpProvider, quantx_core.exceptions.BackendUnavailableError
Implements: Mandatory full-stack end-to-end test for SR-6 (custody backend failure surfaces typed error, no silent fallback)
Outside: Every other numbered SR item
Inside: Wire KeyWallet with an unavailable custody backend into TotpProvider and confirm BackendUnavailableError reaches caller
Wire format: Storage exceptions
Security notes: Mandatory SR-6 end-to-end confirmation across quantx-wallet and quantx-authenticator
"""

from __future__ import annotations

import pytest
from quantx_authenticator.totp_provider import TotpProvider
from quantx_core.exceptions import BackendUnavailableError
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_rate_limiter import InMemoryRateLimiter
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.system_clock import SystemClock
from quantx_wallet.backends.os_keychain_backend import OSKeychainBackend
from quantx_wallet.key_wallet import KeyWallet


def test_sr_06_end_to_end_custody_backend_failure_raises_explicit_error() -> None:
    # 1. Initialize OSKeychainBackend forced to unavailable
    failing_backend = OSKeychainBackend(
        service_name="quantx_test_unavailable", force_unavailable=True
    )
    wallet = KeyWallet(backend=failing_backend)

    # 2. Wire KeyWallet as the secret storage for TotpProvider
    clock = SystemClock()
    kv_store = InMemoryKVStore(clock=clock, max_entries=1000)
    replay_store = InMemoryReplayStore(kv_store=kv_store)
    rate_limiter = InMemoryRateLimiter(kv_store=kv_store, clock=clock, limit=100, window_seconds=60)

    totp = TotpProvider(
        rate_limiter=rate_limiter,
        clock=clock,
        replay_store=replay_store,
        wallet=wallet,
    )

    # 3. Requesting TOTP verification with unavailable custody backend must raise BackendUnavailableError, never silent fallback
    with pytest.raises(BackendUnavailableError, match="not available"):
        totp.verify(subject_id="alice@corp.internal", code="123456")
