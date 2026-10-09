#!/usr/bin/env python3
"""
Lint check: confirms nothing outside jcs_canonicalizer.py serializes structured
data for signing (SR-8, FR-0.4).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

FORBIDDEN_SERIALIZATIONS = [
    "json.dumps",
    "json.dump",
    "pickle.dumps",
    "pickle.dump",
    "yaml.dump",
    "toml.dumps",
    "cbor.dumps",
    "msgpack.packb",
]


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    # jcs_canonicalizer.py is the canonical path
    if path.name == "jcs_canonicalizer.py":
        return errors
    # Exclude test files, linters, and tools
    if "tests" in path.parts or "tools" in path.parts:
        return errors

    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(path))
    except Exception as exc:
        return [f"{path}: failed to parse syntax: {exc}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = ""
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    call_name = f"{node.func.value.id}.{node.func.attr}"
            elif isinstance(node.func, ast.Name):
                call_name = node.func.id

            if call_name in FORBIDDEN_SERIALIZATIONS:
                # If doing serialization in a signing/canonicalization context
                # Flag if serializing dictionary/mappings directly instead of using Canonicalizer
                errors.append(
                    f"{path}:{getattr(node, 'lineno', 0)}: Direct structured serialization call '{call_name}' "
                    f"detected outside jcs_canonicalizer.py. All canonicalization must pass through Canonicalizer (SR-8)."
                )

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent
    targets = [repo_root / "packages", repo_root / "service"]
    all_errors: list[str] = []

    for target in targets:
        if not target.exists():
            continue
        for py_path in target.rglob("*.py"):
            errs = check_file(py_path)
            all_errors.extend(errs)

    if all_errors:
        print("Single canonicalization path check failed with errors:")
        for err in all_errors:
            print(f"  {err}")
        return 1

    print("Single canonicalization path check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
