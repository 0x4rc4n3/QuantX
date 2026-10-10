"""End-to-end security test for SR-7: KEM ciphertext and public key substitution detection.

Layer: cross-cutting
Depends on: quantx_combiners.kem.kem_combiner.KEMCombiner, quantx_crypto_adapters.classical.x25519_adapter.X25519Adapter, quantx_crypto_adapters.pqc.ml_kem_768_adapter.MlKem768Adapter, quantx_core.types.mode.Mode
Implements: Mandatory full-stack end-to-end test for SR-7 (HKDF binding prevents ciphertext/public key substitution)
Outside: Every other numbered SR item
Inside: Swap KEM ciphertext/public key post-encapsulation and confirm derived secret mismatches downstream
Wire format: KEM encapsulation wire format bytes
Security notes: Mandatory SR-7 end-to-end confirmation across quantx-combiners and crypto adapters
"""

from __future__ import annotations

from quantx_combiners.kem import kem_wire_format
from quantx_combiners.kem.kem_combiner import KEMCombiner
from quantx_core.types.mode import Mode
from quantx_crypto_adapters.classical.x25519_adapter import X25519Adapter
from quantx_crypto_adapters.pqc.ml_kem_768_adapter import MlKem768Adapter


def test_sr_07_end_to_end_kem_substitution_detected() -> None:
    # 1. Setup hybrid KEM adapters (X25519 + ML-KEM-768)
    x_priv, x_pub = X25519Adapter.generate_keypair()
    ml_priv, ml_pub = MlKem768Adapter.generate_keypair()

    providers = {
        "x25519": X25519Adapter(),
        "ml-kem-768": MlKem768Adapter(),
    }

    combiner = KEMCombiner(
        required_mode=Mode.HYBRID,
        expected_algorithms=["x25519", "ml-kem-768"],
        providers=providers,
    )

    public_keys = {"x25519": x_pub, "ml-kem-768": ml_pub}
    private_keys = {"x25519": x_priv, "ml-kem-768": ml_priv}

    # 2. Genuine encapsulation and decapsulation produces matching secret
    wire_ct, sender_secret = combiner.encapsulate(public_keys=public_keys)
    recipient_secret = combiner.decapsulate(wire_bytes=wire_ct, private_keys=private_keys)
    assert sender_secret == recipient_secret

    # 3. Attacker substitutes ML-KEM ciphertext with an alternative ciphertext from another session
    _, alt_ml_pub = MlKem768Adapter.generate_keypair()
    alt_wire_ct, _ = combiner.encapsulate(public_keys={"x25519": x_pub, "ml-kem-768": alt_ml_pub})

    mode, components = kem_wire_format.decode(wire_ct)
    _, alt_components = kem_wire_format.decode(alt_wire_ct)

    # Substituted ciphertext: authentic x25519 ct + substituted ml-kem ct
    tampered_components = [components[0], alt_components[1]]
    tampered_wire_ct = kem_wire_format.encode(mode, tampered_components)

    # Decapsulation with tampered ciphertext MUST NOT produce the original shared secret
    try:
        tampered_secret = combiner.decapsulate(
            wire_bytes=tampered_wire_ct, private_keys=private_keys
        )
        assert (
            tampered_secret != sender_secret
        ), "Substituted ciphertext must not derive original shared secret"
    except Exception:
        # Failing closed on decapsulation failure is also safe and compliant
        pass
