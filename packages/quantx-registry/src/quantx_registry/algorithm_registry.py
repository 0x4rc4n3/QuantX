"""
Layer: 3
Depends on: Every Layer-1 adapter (exception to FR-X.2); SignatureCombiner, KEMCombiner (Layer 2); this package's own role/loader/signature files
Implements: resolve(role_name: str) -> tuple[SignatureCombiner, KEMCombiner, Mode]
Outside: Loading/parsing the YAML file itself (registry_config_loader.py); verifying the config's signature (registry_config_signature.py); defining what a role is as a value (registry_role.py).
Inside: Resolving a role name to a concrete, constructed combiner pair, using adapters it alone is permitted to import directly.
Security notes: FR-3.3: unsigned config only for allow_unsigned=True dev/demo use; the signed-config path is what any non-dev deployment uses and rejects unsigned config by default. GATE_REVIEW_REQUIRED component.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import yaml
from quantx_combiners.kem.kem_combiner import KEMCombiner
from quantx_combiners.signature.signature_combiner import SignatureCombiner
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.interfaces.canonicalizer import Canonicalizer
from quantx_core.interfaces.kem_provider import KEMProvider
from quantx_core.interfaces.verifier import Verifier
from quantx_core.types.algorithm_id import AlgorithmId
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.ecdsa_p256_adapter import EcdsaP256Adapter
from quantx_crypto_adapters.classical.ed25519_adapter import Ed25519Adapter
from quantx_crypto_adapters.classical.x25519_adapter import X25519Adapter
from quantx_crypto_adapters.pqc.ml_dsa_65_adapter import MlDsa65Adapter
from quantx_crypto_adapters.pqc.ml_dsa_87_adapter import MlDsa87Adapter
from quantx_crypto_adapters.pqc.ml_kem_768_adapter import MlKem768Adapter
from quantx_crypto_adapters.pqc.ml_kem_1024_adapter import MlKem1024Adapter

from quantx_registry import registry_config_loader, registry_config_signature
from quantx_registry.registry_role import RegistryRole

# Map algorithm identifiers to factory callables or adapter classes
SIGNATURE_ADAPTER_MAP: dict[AlgorithmId, type] = {
    AlgorithmId.ED25519: Ed25519Adapter,
    AlgorithmId.ECDSA_P256: EcdsaP256Adapter,
    AlgorithmId.ML_DSA_65: MlDsa65Adapter,
    AlgorithmId.ML_DSA_87: MlDsa87Adapter,
}

KEM_ADAPTER_MAP: dict[AlgorithmId, type] = {
    AlgorithmId.X25519: X25519Adapter,
    AlgorithmId.ML_KEM_768: MlKem768Adapter,
    AlgorithmId.ML_KEM_1024: MlKem1024Adapter,
}


class AlgorithmRegistry:
    """
    AlgorithmRegistry resolves named roles to wired SignatureCombiner and KEMCombiner instances (FR-3.1).
    Enforces signed configuration files by default unless allow_unsigned=True is explicitly set.
    """

    def __init__(
        self,
        config_path: Path | str,
        allow_unsigned: bool = False,
        config_signature: bytes | None = None,
        config_verifier: Verifier | None = None,
        canonicalizer: Canonicalizer | None = None,
        verifiers_by_alg: Mapping[str, Verifier] | None = None,
        kem_providers_by_alg: Mapping[str, KEMProvider] | None = None,
    ) -> None:
        self._allow_unsigned = allow_unsigned
        self._verifiers_by_alg = dict(verifiers_by_alg or {})
        self._kem_providers_by_alg = dict(kem_providers_by_alg or {})

        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config path does not exist: {path}")

        raw_yaml = path.read_text(encoding="utf-8")
        try:
            config_dict = yaml.safe_load(raw_yaml)
        except Exception as exc:
            raise MalformedInputError(f"Failed to parse YAML config: {exc}") from exc

        # Check signature unless explicitly allowed unsigned
        if not allow_unsigned:
            if config_signature is None or config_verifier is None or canonicalizer is None:
                raise MalformedInputError(
                    "Signed configuration required: config_signature, config_verifier, and canonicalizer must be provided when allow_unsigned=False (FR-3.3)"
                )
            if not registry_config_signature.verify(
                config_data=config_dict,
                signature=config_signature,
                verifier=config_verifier,
                canonicalizer=canonicalizer,
            ):
                raise MalformedInputError("Configuration signature verification failed (FR-3.3)")

        # Load roles
        roles = registry_config_loader.parse_roles_data(config_dict)
        self._roles: dict[str, RegistryRole] = {}
        for role in roles:
            # Check algorithm availability
            for sig_alg in role.signature_algorithms:
                if sig_alg not in SIGNATURE_ADAPTER_MAP:
                    raise MalformedInputError(
                        f"Role '{role.role_id}' references unavailable signature adapter '{sig_alg.value}'"
                    )
            for kem_alg in role.kem_algorithms:
                if kem_alg not in KEM_ADAPTER_MAP:
                    raise MalformedInputError(
                        f"Role '{role.role_id}' references unavailable KEM adapter '{kem_alg.value}'"
                    )
            self._roles[role.role_id] = role

    @property
    def roles(self) -> dict[str, RegistryRole]:
        return dict(self._roles)

    def get_role(self, role_id: str) -> RegistryRole:
        if role_id not in self._roles:
            raise KeyError(f"Unknown registry role: '{role_id}'")
        return self._roles[role_id]

    def resolve(
        self,
        role_id: str,
        custom_verifiers: Mapping[str, Verifier] | None = None,
        custom_kem_providers: Mapping[str, KEMProvider] | None = None,
    ) -> tuple[SignatureCombiner, KEMCombiner, Mode]:
        """
        Resolves a role name to a configured SignatureCombiner, KEMCombiner, and Mode.
        """
        role = self.get_role(role_id)

        # Wire signature verifiers
        sig_verifiers: dict[str, Verifier] = {}
        expected_sig_algs: list[str] = []
        for alg_enum in role.signature_algorithms:
            alg_name = alg_enum.value
            expected_sig_algs.append(alg_name)
            if custom_verifiers and alg_name in custom_verifiers:
                sig_verifiers[alg_name] = custom_verifiers[alg_name]
            elif alg_name in self._verifiers_by_alg:
                sig_verifiers[alg_name] = self._verifiers_by_alg[alg_name]
            else:
                adapter_cls = SIGNATURE_ADAPTER_MAP[alg_enum]
                sig_verifiers[alg_name] = adapter_cls()

        sig_combiner = SignatureCombiner(
            required_mode=role.required_mode,
            role_id=role.role_id,
            expected_algorithms=expected_sig_algs,
            verifiers=sig_verifiers,
        )

        # Wire KEM providers
        kem_providers: dict[str, KEMProvider] = {}
        expected_kem_algs: list[str] = []
        for alg_enum in role.kem_algorithms:
            alg_name = alg_enum.value
            expected_kem_algs.append(alg_name)
            if custom_kem_providers and alg_name in custom_kem_providers:
                kem_providers[alg_name] = custom_kem_providers[alg_name]
            elif alg_name in self._kem_providers_by_alg:
                kem_providers[alg_name] = self._kem_providers_by_alg[alg_name]
            else:
                kem_adapter_cls = KEM_ADAPTER_MAP[alg_enum]
                kem_providers[alg_name] = kem_adapter_cls()

        kem_combiner = KEMCombiner(
            required_mode=role.required_mode,
            expected_algorithms=expected_kem_algs,
            providers=kem_providers,
        )

        return sig_combiner, kem_combiner, role.required_mode
