#!/usr/bin/env python3
"""
Lint check: validates that module docstrings in packages/ and service/
follow the required docstring contract in order:
Layer, Depends on, Implements, Outside, Inside, [Wire format], Security notes.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REQUIRED_ORDER = [
    "Layer",
    "Depends on",
    "Implements",
    "Outside",
    "Inside",
    "Wire format",
    "Security notes",
]

MANDATORY_FIELDS = [
    "Layer",
    "Depends on",
    "Implements",
    "Outside",
    "Inside",
]


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    if path.name == "__init__.py":
        return errors  # __init__.py files are package markers

    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(path))
    except Exception as exc:
        return [f"{path}: failed to parse syntax: {exc}"]

    docstring = ast.get_docstring(tree)
    if not docstring:
        return [f"{path}: missing module docstring"]

    found_fields: list[tuple[str, int]] = []
    for field in REQUIRED_ORDER:
        pattern = rf"(?:^|\n)\s*(?:[-*]\s*)?{re.escape(field)}[\s*:]"
        match = re.search(pattern, docstring, re.IGNORECASE)
        if match:
            found_fields.append((field, match.start()))

    # Check mandatory fields
    present_field_names = {f[0] for f in found_fields}
    for req in MANDATORY_FIELDS:
        if req not in present_field_names:
            errors.append(f"{path}: missing mandatory docstring contract field '{req}'")

    # Check ordering
    indices = [REQUIRED_ORDER.index(f[0]) for f in found_fields]
    if indices != sorted(indices):
        order_str = " -> ".join(f[0] for f in found_fields)
        errors.append(f"{path}: docstring contract fields out of required order: {order_str}")

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
        print("Docstring contract check failed with errors:")
        for err in all_errors:
            print(f"  {err}")
        return 1

    print("Docstring contract check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
