#!/usr/bin/env python3
"""
Lint check: confirms no component above Layer 1 imports a sibling concrete class
instead of a Layer-0 interface, except AlgorithmRegistry (FR-X.2, FR-3.1).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# Packages and their assigned layers
PACKAGE_LAYERS: dict[str, int] = {
    "quantx_core": 0,
    "quantx_crypto_adapters": 1,
    "quantx_combiners": 2,
    "quantx_registry": 3,
    "quantx_session": 4,
    "quantx_authenticator": 5,
    "quantx_wallet": 6,
    "quantx_threshold": 8,
    "quantx_zkp": 9,
    "quantx_compliance": 10,
    "quantx_service": 11,
}


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    # Tests are permitted to import test subjects and fixtures
    if "tests" in path.parts:
        return errors

    # AlgorithmRegistry is the sole permitted exception
    if path.name == "algorithm_registry.py":
        return errors

    # Determine caller layer
    caller_pkg = None
    for part in path.parts:
        if part in PACKAGE_LAYERS:
            caller_pkg = part
            break

    if not caller_pkg:
        return errors

    caller_layer = PACKAGE_LAYERS[caller_pkg]
    if caller_layer <= 1:
        return errors  # Layer 0 and Layer 1 are allowed

    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(path))
    except Exception as exc:
        return [f"{path}: failed to parse syntax: {exc}"]

    for node in ast.walk(tree):
        imported_module = ""
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_module = alias.name
                check_import(imported_module, caller_pkg, caller_layer, path, errors)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_module = node.module
                check_import(imported_module, caller_pkg, caller_layer, path, errors)

    return errors


def check_import(
    module: str,
    caller_pkg: str,
    caller_layer: int,
    path: Path,
    errors: list[str],
) -> None:
    # Check if importing from another quantx package
    for target_pkg, target_layer in PACKAGE_LAYERS.items():
        if module == target_pkg or module.startswith(f"{target_pkg}."):
            # Importing Layer 0 is always allowed
            if target_layer == 0:
                continue

            # Importing sibling concrete package at same layer or lower non-Layer-0 layer
            if target_layer == caller_layer and target_pkg != caller_pkg:
                errors.append(
                    f"{path}: forbidden sibling import from '{module}' (layer {target_layer})"
                )
            elif 1 <= target_layer < caller_layer:
                # E.g. Layer 2 importing Layer 1 adapter concrete classes directly
                errors.append(
                    f"{path}: forbidden import from lower concrete layer '{module}' (layer {target_layer}) - must depend on Layer 0 interfaces only"
                )


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
        print("Sibling concrete imports check failed with errors:")
        for err in all_errors:
            print(f"  {err}")
        return 1

    print("Sibling concrete imports check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
