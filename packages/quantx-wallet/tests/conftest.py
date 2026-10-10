"""Shared test fixtures for quantx-wallet test suite.

Layer: 6-7
Depends on: quantx_core, quantx_wallet
Implements: Pytest fixtures for backends, key wallets, recovery managers, and corrupted vaults
Outside: Test assertion logic
Inside: Fixture provisioning for unit and security suites
Security notes: Provides fixtures for SR-06, SR-09, SR-11 verification.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from quantx_core.impls.in_memory_kv_store import InMemoryKVStore
from quantx_core.impls.in_memory_replay_store import InMemoryReplayStore
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer
from quantx_core.interfaces.clock import Clock
from quantx_wallet.backends.encrypted_file_backend import EncryptedFileBackend


class FakeClock(Clock):
    """Controllable clock for wallet test fixtures."""

    def __init__(self, start_time: datetime | None = None) -> None:
        self._current_time = start_time or datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._current_time

    def set_time(self, new_time: datetime) -> None:
        self._current_time = new_time


class MockKeyringProvider:
    """Mock OS Keychain service provider."""

    def __init__(self) -> None:
        self.passwords: dict[tuple[str, str], str] = {}

    def set_password(self, service: str, username: str, password: str) -> None:
        self.passwords[(service, username)] = password

    def get_password(self, service: str, username: str) -> str | None:
        return self.passwords.get((service, username))


class MockHsmSession:
    """Mock PKCS#11 session simulating token-resident keys."""

    def __init__(self, key_id: str = "test-key-1") -> None:
        self.keys: dict[str, bytes] = {key_id: b"mock-public-key-bytes"}
        self.signatures: dict[str, bytes] = {}

    def get_algorithm(self, key_id: str) -> str:
        return "ed25519"

    def generate_keypair(self, key_id: str, algorithm: str) -> bytes:
        pub = f"pub-{key_id}-{algorithm}".encode("utf-8")
        self.keys[key_id] = pub
        return pub

    def sign(self, key_id: str, message: bytes) -> bytes:
        sig = f"sig-for-{key_id}:{len(message)}".encode("utf-8")
        self.signatures[key_id] = sig
        return sig

    def decapsulate(self, key_id: str, ciphertext: bytes) -> bytes:
        return f"shared-secret-for-{key_id}".encode("utf-8")


class MockAwsKmsClient:
    """Mock AWS KMS client."""

    def __init__(self) -> None:
        self.keys: dict[str, dict[str, Any]] = {}

    def create_key(self, Description: str = "") -> dict[str, Any]:
        arn = f"arn:aws:kms:us-east-1:123456789012:key/mock-{len(self.keys) + 1}"
        self.keys[arn] = {"Description": Description}
        return {"KeyMetadata": {"Arn": arn}}

    def get_public_key(self, KeyId: str) -> dict[str, Any]:
        return {"PublicKey": b"mock-aws-kms-public-key"}

    def sign(
        self,
        KeyId: str,
        Message: bytes,
        MessageType: str,
        SigningAlgorithm: str,
    ) -> dict[str, Any]:
        return {"Signature": b"mock-aws-kms-signature"}


class MockGcpKmsClient:
    """Mock GCP KMS client."""

    def __init__(self) -> None:
        self.keys: dict[str, Any] = {}

    def create_crypto_key(self, parent: str, crypto_key_id: str, crypto_key: dict[str, Any]) -> Any:
        class CryptoKey:
            name = f"{parent}/cryptoKeys/{crypto_key_id}"

        return CryptoKey()

    def get_public_key(self, name: str) -> Any:
        class PublicKey:
            pem = "-----BEGIN PUBLIC KEY-----\nMOCK\n-----END PUBLIC KEY-----"

        return PublicKey()

    def asymmetric_sign(self, name: str, data: bytes) -> Any:
        class SignResponse:
            signature = b"mock-gcp-kms-signature"

        return SignResponse()

    def asymmetric_decrypt(self, name: str, ciphertext: bytes) -> Any:
        class DecryptResponse:
            plaintext = b"mock-gcp-kms-plaintext"

        return DecryptResponse()


@pytest.fixture
def fake_clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def master_key() -> bytes:
    return b"\x01" * 32


@pytest.fixture
def canonicalizer() -> JCSCanonicalizer:
    return JCSCanonicalizer()


@pytest.fixture
def kv_store(fake_clock: FakeClock) -> InMemoryKVStore:
    return InMemoryKVStore(clock=fake_clock)


@pytest.fixture
def replay_store(kv_store: InMemoryKVStore) -> InMemoryReplayStore:
    return InMemoryReplayStore(kv_store=kv_store)


@pytest.fixture
def encrypted_file_backend(
    tmp_path: Path,
    master_key: bytes,
    canonicalizer: JCSCanonicalizer,
) -> EncryptedFileBackend:
    return EncryptedFileBackend(
        base_dir=tmp_path / "vault",
        master_key=master_key,
        canonicalizer=canonicalizer,
    )
