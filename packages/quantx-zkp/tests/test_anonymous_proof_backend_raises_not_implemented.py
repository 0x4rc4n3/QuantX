"""Unit test guarding D9: AnonymousProofBackend raises NotImplementedError.

Layer: 9
Depends on: quantx_zkp.anonymous_proof_backend.AnonymousProofBackend
Implements: Pytest tests validating that all AnonymousProofBackend methods raise NotImplementedError
Outside: Merkle membership proofs
Inside: Method invocation checks ensuring deliberate failure closed pending external audit
Security notes: D9 / FR-9.2: Tripwire ensuring no unaudited homegrown zk-SNARK is shipped.
"""

from __future__ import annotations

import pytest
from quantx_zkp.anonymous_proof_backend import AnonymousProofBackend


def test_anonymous_proof_backend_raises_not_implemented() -> None:
    backend = AnonymousProofBackend()

    with pytest.raises(NotImplementedError, match="pending funded, scoped external audit"):
        backend.generate_proof(b"secret", b"public-input")

    with pytest.raises(NotImplementedError, match="pending funded, scoped external audit"):
        backend.verify_proof(b"proof-bytes", b"public-input")
