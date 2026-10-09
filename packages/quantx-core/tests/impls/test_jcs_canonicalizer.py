"""
Layer: 0
Depends on: quantx_core.impls.jcs_canonicalizer.JCSCanonicalizer, quantx_core.exceptions.malformed_input_error.MalformedInputError
Implements: pytest test functions for JCSCanonicalizer
Outside: Testing anything other than JCSCanonicalizer.
Inside: Determinism across key insertion order, repeatability, nested structures, and invalid input rejection.
Security notes: Foundation testing for SR-8 single canonicalization path.
"""

from __future__ import annotations

import pytest
from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.impls.jcs_canonicalizer import JCSCanonicalizer


def test_jcs_canonicalizer_key_order_independence() -> None:
    c = JCSCanonicalizer()
    map1 = {"b": 2, "a": 1, "c": [3, 2, 1]}
    map2 = {"c": [3, 2, 1], "a": 1, "b": 2}

    res1 = c.canonicalize(map1)
    res2 = c.canonicalize(map2)

    assert res1 == res2
    assert res1 == b'{"a":1,"b":2,"c":[3,2,1]}'


def test_jcs_canonicalizer_stability_and_determinism() -> None:
    c = JCSCanonicalizer()
    data = {
        "issuer": "QuantX",
        "nested": {"z": True, "y": None, "x": False},
        "count": 42,
    }
    expected = b'{"count":42,"issuer":"QuantX","nested":{"x":false,"y":null,"z":true}}'
    assert c.canonicalize(data) == expected
    # Multiple runs produce identical byte outputs
    for _ in range(10):
        assert c.canonicalize(data) == expected


def test_jcs_canonicalizer_invalid_inputs() -> None:
    c = JCSCanonicalizer()
    # Non-mapping top-level input
    with pytest.raises(MalformedInputError):
        c.canonicalize([1, 2, 3])  # type: ignore[arg-type]

    # Non-string dictionary keys
    with pytest.raises(MalformedInputError):
        c.canonicalize({1: "invalid"})  # type: ignore[dict-item]
