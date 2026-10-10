"""
Layer: 3
Depends on: Signer/Verifier (Layer 0), Canonicalizer (Layer 0, FR-0.4)
Implements: sign(config_data: Mapping[str, Any], signer: Signer, canonicalizer: Canonicalizer) -> bytes; verify(config_data: Mapping[str, Any], signature: bytes, verifier: Verifier, canonicalizer: Canonicalizer) -> bool
Outside: Deciding whether signing is required for a given deployment — that's algorithm_registry.py's allow_unsigned flag.
Inside: The sign/verify operations over canonicalized configuration data using Layer 0 interfaces.
Security notes: FR-3.3 / SR-1-adjacent: ensures config integrity and provenance. Canonicalizes exclusively via Canonicalizer (RFC 8785).
"""

from __future__ import annotations

from typing import Any, Mapping

from quantx_core.interfaces.canonicalizer import Canonicalizer
from quantx_core.interfaces.signer import Signer
from quantx_core.interfaces.verifier import Verifier


def sign(
    config_data: Mapping[str, Any],
    signer: Signer,
    canonicalizer: Canonicalizer,
) -> bytes:
    """
    Canonicalize the configuration dictionary using Canonicalizer and sign it.
    """
    canonical_bytes = canonicalizer.canonicalize(config_data)
    return signer.sign(canonical_bytes)


def verify(
    config_data: Mapping[str, Any],
    signature: bytes,
    verifier: Verifier,
    canonicalizer: Canonicalizer,
) -> bool:
    """
    Canonicalize the configuration dictionary and verify its signature.
    Fails closed on any error, returning False.
    """
    try:
        canonical_bytes = canonicalizer.canonicalize(config_data)
        return verifier.verify(canonical_bytes, signature)
    except Exception:
        return False
