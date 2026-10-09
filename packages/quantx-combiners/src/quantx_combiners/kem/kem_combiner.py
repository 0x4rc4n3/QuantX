"""
Layer: 2
Depends on: KEMProvider (Layer 0), Mode (Layer 0), kem_wire_format.py, kem_hkdf_binding.py
Implements: combine(wire_bytes: bytes) -> bytes (derived shared secret) or an equivalent encapsulate/decapsulate-combining pair
Outside: Wire encoding/decoding itself; the HKDF-binding computation itself.
Inside: Orchestration: parse -> decapsulate each required component -> derive the combined shared secret via kem_hkdf_binding.py.
Security notes: Implements FR-2.4/SR-7 by delegating the actual binding computation to kem_hkdf_binding.py. GATE_REVIEW_REQUIRED component.
"""

from __future__ import annotations

from typing import Mapping, Sequence, Tuple

from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.interfaces.kem_provider import KEMProvider
from quantx_core.types.mode import Mode

from quantx_combiners.kem import kem_hkdf_binding, kem_wire_format


class KEMCombiner:
    """
    Generic KEMCombiner orchestrating wire parsing, decapsulation with configured
    Layer 0 KEMProvider instances, and HKDF ciphertext/public-key binding (FR-2.2, SR-7).
    """

    def __init__(
        self,
        required_mode: Mode,
        expected_algorithms: Sequence[str],
        providers: Mapping[str, KEMProvider],
    ) -> None:
        self._required_mode = required_mode
        self._expected_algorithms = tuple(expected_algorithms)
        self._providers = dict(providers)

        expected_cnt = 2 if required_mode == Mode.HYBRID else 1
        if len(self._expected_algorithms) != expected_cnt:
            raise ValueError(
                f"Expected algorithm count {len(self._expected_algorithms)} does not match mode {required_mode.value}"
            )
        for alg in self._expected_algorithms:
            if alg not in self._providers:
                raise ValueError(f"Missing KEMProvider for expected algorithm '{alg}'")

    @property
    def required_mode(self) -> Mode:
        return self._required_mode

    @property
    def expected_algorithms(self) -> tuple[str, ...]:
        return self._expected_algorithms

    def encapsulate(
        self,
        public_keys: Mapping[str, bytes],
    ) -> tuple[bytes, bytes]:
        """
        Encapsulate shared secret(s) against provided public keys for each expected algorithm.

        Returns:
            (wire_bytes, combined_shared_secret)
        """
        components: list[Tuple[str, bytes, bytes]] = []
        shared_secrets: list[bytes] = []

        for alg_id in self._expected_algorithms:
            if alg_id not in public_keys:
                raise MalformedInputError(f"Missing public key for expected algorithm '{alg_id}'")
            pub_key = public_keys[alg_id]
            provider = self._providers[alg_id]
            ciphertext, shared_secret = provider.encapsulate(pub_key)
            if not ciphertext or not shared_secret:
                raise MalformedInputError(f"Encapsulation failed for algorithm '{alg_id}'")
            components.append((alg_id, pub_key, ciphertext))
            shared_secrets.append(shared_secret)

        wire_bytes = kem_wire_format.encode(self._required_mode, components)
        combined_secret = kem_hkdf_binding.derive(shared_secrets, components)
        return wire_bytes, combined_secret

    def decapsulate(
        self,
        wire_bytes: bytes,
        private_keys: Mapping[str, bytes],
    ) -> bytes:
        """
        Decapsulate combined KEM wire bytes and derive the bound shared secret.

        Fails closed by returning b"" or raising MalformedInputError on any invalid
        or mismatched input.
        """
        declared_mode, components = kem_wire_format.decode(wire_bytes)

        if declared_mode != self._required_mode:
            raise MalformedInputError(
                f"Declared mode '{declared_mode.value}' does not match required mode '{self._required_mode.value}'"
            )

        parsed_algs = tuple(alg for alg, _, _ in components)
        if parsed_algs != self._expected_algorithms:
            raise MalformedInputError(
                f"Parsed algorithms {parsed_algs} do not match expected algorithms {self._expected_algorithms}"
            )

        shared_secrets: list[bytes] = []
        for alg_id, _, ct in components:
            if alg_id not in private_keys:
                raise MalformedInputError(f"Missing private key for algorithm '{alg_id}'")
            priv_key = private_keys[alg_id]
            provider = self._providers[alg_id]
            ss = provider.decapsulate(ct, priv_key)
            if not ss:
                # Decapsulation failed on provider leg -> fail closed
                return b""
            shared_secrets.append(ss)

        return kem_hkdf_binding.derive(shared_secrets, components)

    def combine(
        self,
        wire_bytes: bytes,
        private_keys: Mapping[str, bytes],
    ) -> bytes:
        """Alias for decapsulate to satisfy the combine() contract."""
        return self.decapsulate(wire_bytes, private_keys)
