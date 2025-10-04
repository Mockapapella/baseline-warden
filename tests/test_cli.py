from pathlib import Path

from typer.testing import CliRunner

from baseline_warden.cli import app
from baseline_warden.index.cache import BaselineLock, write_lock

CONFIG_TEMPLATE = """
[policy]
required_status = "newly_or_widely"
unknown_behavior = "warn"

[include]
paths = ["src/**"]

[ignore]
globs = []

[output]
formats = ["console"]
"""


def _write_config(path: Path) -> Path:
    config_path = path / "baseline-warden.toml"
    config_path.write_text(CONFIG_TEMPLATE)
    return config_path


def test_scan_requires_lock(tmp_path: Path) -> None:
    runner = CliRunner()
    config_path = _write_config(tmp_path)
    result = runner.invoke(
        app,
        ["scan", "--dry-run", "--config", str(config_path), "--lock-path", str(tmp_path / "missing.lock.json")],
        catch_exceptions=False,
    )
    assert result.exit_code == 2
    assert "Lock file not found" in result.stdout


def test_scan_with_lock(tmp_path: Path) -> None:
    runner = CliRunner()
    config_path = _write_config(tmp_path)
    lock_path = tmp_path / "baseline.lock.json"
    write_lock(lock_path, BaselineLock())

    result = runner.invoke(
        app,
        ["scan", "--dry-run", "--config", str(config_path), "--lock-path", str(lock_path)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Lock snapshot" in result.stdout
