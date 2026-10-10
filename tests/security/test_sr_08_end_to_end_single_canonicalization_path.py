"""End-to-end security test for SR-8: Single canonicalization path used for all signed data.

Layer: cross-cutting
Depends on: quantx_core.impls.jcs_canonicalizer.JCSCanonicalizer, quantx_session.default_setup, quantx_registry.registry_config_signature, quantx_wallet.backends.encrypted_file_backend.EncryptedFileBackend
Implements: Mandatory full-stack end-to-end test for SR-8 (single canonicalization path via JCSCanonicalizer)
Outside: Every other numbered SR item
Inside: Instrument JCSCanonicalizer and confirm all signed/authenticated structures route through it
Wire format: Canonical JSON RFC 8785 bytes
Security notes: Mandatory SR-8 end-to-end confirmation across quantx-core, quantx-session, and quantx-registry
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.impls.system_clock import SystemClock
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_registry import registry_config_signature
from quantx_session.challenge_issuer import ChallengeIssuer
from quantx_wallet.backends.encrypted_file_backend import EncryptedFileBackend
from quantx_wallet.vault_metadata import VaultMetadata


def test_sr_08_end_to_end_single_canonicalization_path(tmp_path: Path) -> None:
    canonicalizer = JCSCanonicalizer()
    clock = SystemClock()
    kv_store = InMemoryKVStore(clock=clock, max_entries=1000)

    with patch.object(
        canonicalizer, "canonicalize", wraps=canonicalizer.canonicalize
    ) as spy_canonicalize:
        # 1. Challenge creation routes through JCSCanonicalizer
        issuer = ChallengeIssuer(
            kv_store=kv_store,
            clock=clock,
            canonicalizer=canonicalizer,
            role_modes={"session-auth": Mode.HYBRID},
        )
        record = issuer.issue(role_id="session-auth", subject_id="alice@corp.internal")
        assert record is not None
        assert spy_canonicalize.call_count >= 1

        # 2. Signed configuration signing & verification routes through JCSCanonicalizer
        calls_before = spy_canonicalize.call_count
        ed_priv, ed_pub = Ed25519Adapter.generate_keypair()
        signer = Ed25519Adapter(private_key=ed_priv)
        verifier = Ed25519Adapter(public_key=ed_pub)

        config_data = {
            "schema_version": 1,
            "roles": [{"role_id": "test", "mode": "HYBRID", "algorithms": ["ed25519"]}],
        }
        sig = registry_config_signature.sign(config_data, signer, canonicalizer)
        assert registry_config_signature.verify(config_data, sig, verifier, canonicalizer) is True
        assert spy_canonicalize.call_count > calls_before

        # 3. Vault metadata AEAD authentication routes through JCSCanonicalizer
        calls_before_vault = spy_canonicalize.call_count
        master_key = b"0" * 32
        backend = EncryptedFileBackend(
            base_dir=tmp_path, master_key=master_key, canonicalizer=canonicalizer
        )
        meta = VaultMetadata(key_id="k-1", algorithm="ed25519", created_at="2026-10-10T00:00:00Z")
        backend.store("k-1", b"secret-material", meta)
        assert spy_canonicalize.call_count > calls_before_vault
