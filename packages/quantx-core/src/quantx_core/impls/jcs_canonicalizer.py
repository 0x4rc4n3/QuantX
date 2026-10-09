"""
Layer: 0
Depends on: quantx_core.interfaces.canonicalizer.Canonicalizer, quantx_core.exceptions.malformed_input_error.MalformedInputError
Implements: JCSCanonicalizer
Outside: Anything not directly part of the Canonicalizer contract.
Inside: RFC 8785 JSON Canonicalization Scheme implementation.
Wire format: RFC 8785 (JCS) - deterministic key ordering, no insignificant whitespace.
Security notes: SR-8 / FR-0.4. Exactly one canonicalization path is used for anything signed, system-wide.
"""

from __future__ import annotations

import json
import math
from typing import Any, Mapping

from quantx_core.exceptions.malformed_input_error import MalformedInputError
from quantx_core.interfaces.canonicalizer import Canonicalizer


class JCSCanonicalizer(Canonicalizer):
    """
    Reference RFC 8785 JSON Canonicalization Scheme (JCS) implementation.
    The sole authorized canonicalization path in QuantX (SR-8).
    """

    def canonicalize(self, data: Mapping[str, Any]) -> bytes:
        """
        Deterministically serializes a mapping to bytes according to RFC 8785.
        """
        if not isinstance(data, Mapping):
            raise MalformedInputError(
                f"Data to canonicalize must be a Mapping, got {type(data).__name__}"
            )
        try:
            return self._encode_value(data)
        except Exception as exc:
            if isinstance(exc, MalformedInputError):
                raise
            raise MalformedInputError(f"Failed to canonicalize structured data: {exc}") from exc

    def _encode_value(self, val: Any) -> bytes:
        if val is None:
            return b"null"
        if isinstance(val, bool):
            return b"true" if val else b"false"
        if isinstance(val, int):
            return str(val).encode("utf-8")
        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                raise MalformedInputError(
                    "NaN and Infinity are not permitted in JSON canonicalization"
                )
            # In JCS/ECMAScript, integer-valued floats serialize without .0
            if val.is_integer():
                return str(int(val)).encode("utf-8")
            return json.dumps(val, separators=(",", ":")).encode("utf-8")
        if isinstance(val, str):
            return json.dumps(val, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if isinstance(val, (list, tuple)):
            items = [self._encode_value(item) for item in val]
            return b"[" + b",".join(items) + b"]"
        if isinstance(val, Mapping):
            # Keys must be strings and sorted by UTF-16 code units (RFC 8785 §3.2.3)
            sorted_keys = sorted(val.keys(), key=lambda k: str(k).encode("utf-16-be"))
            members: list[bytes] = []
            for k in sorted_keys:
                if not isinstance(k, str):
                    raise MalformedInputError(
                        f"Object keys must be strings, got {type(k).__name__}"
                    )
                k_bytes = self._encode_value(k)
                v_bytes = self._encode_value(val[k])
                members.append(k_bytes + b":" + v_bytes)
            return b"{" + b",".join(members) + b"}"

        raise MalformedInputError(
            f"Unsupported data type for canonicalization: {type(val).__name__}"
        )
