"""Unit tests for QuantX command-line interface.

Layer: sidecar
Depends on: quantx_service.cli.main, tmp_path
Implements: Pytest tests verifying CLI subcommands init, validate, explain, and run
Outside: Long-running production deployment daemon
Inside: Subcommand execution, exit code verification, file creation, and explain output inspection
Security notes: Confirms init refuses overwriting, validate detects rule breaches, and explain never exposes secrets.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from quantx_service.cli import main


def test_cli_init_recipe_a(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """init --recipe A writes a valid quantx.yaml and refuses to overwrite."""
    monkeypatch.chdir(tmp_path)
    # First invocation succeeds
    ret = main(["init", "--recipe", "A"])
    assert ret == 0
    assert (tmp_path / "quantx.yaml").exists()

    # Second invocation refuses to overwrite with exit 2
    ret2 = main(["init", "--recipe", "A"])
    assert ret2 == 2


def test_cli_validate_recipe_examples(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """validate returns exit 0 for initialized Recipe A, and exit 2 for invalid configs."""
    monkeypatch.chdir(tmp_path)
    main(["init", "--recipe", "A"])

    ret_ok = main(["validate", "--file", "quantx.yaml"])
    assert ret_ok == 0

    # Write broken config
    (tmp_path / "broken.yaml").write_text(
        "unknown_key: true\nschema_version: 1\n", encoding="utf-8"
    )
    ret_err = main(["validate", "--file", "broken.yaml"])
    assert ret_err == 2


def test_cli_explain_no_secrets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """explain prints the resolved wiring and config hash without secret values (CFG-5)."""
    monkeypatch.chdir(tmp_path)
    main(["init", "--recipe", "A"])

    ret = main(["explain", "--file", "quantx.yaml"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "Canonical Config Hash" in captured
    assert "Operating Mode: HYBRID" in captured
    assert "password" not in captured.lower()
    assert "private_key" not in captured.lower()


def test_cli_run_fails_closed_when_backend_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """run exits 3 when a configured backend is unreachable (CFG-3)."""
    monkeypatch.chdir(tmp_path)
    # Configure unresolvable redis backend
    redis_cfg = """schema_version: 1
environment: dev
mode: HYBRID
algorithms:
  signature: {classical: ed25519, pqc: ml-dsa-65}
  kem:       {classical: x25519,  pqc: ml-kem-768}
registry: {config_signing: unsigned}
state: {backend: redis, url_ref: "env:NONEXISTENT_REDIS_URL"}
custody: {backend: memory_raw}
second_factor: [totp]
threshold: {enabled: false}
membership_proof: {backend: none}
compliance: {scanners: []}
service: {auth: bearer, tls_enforcement: off}
"""
    (tmp_path / "redis_fail.yaml").write_text(redis_cfg, encoding="utf-8")
    ret = main(["run", "--file", "redis_fail.yaml"])
    assert ret == 3
