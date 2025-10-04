from pathlib import Path

from typer.testing import CliRunner

from baseline_warden.cli import app
from baseline_warden.index.cache import BaselineLock, write_lock


def test_paths_override_limits_scan_scope(tmp_path: Path) -> None:
    (tmp_path / "core" / "templates").mkdir(parents=True)
    (tmp_path / "core" / "static").mkdir(parents=True)
    (tmp_path / "core" / "templates" / "index.html").write_text("<p>ok</p>")
    (tmp_path / "core" / "static" / "main.css").write_text("body { margin: 0; }")

    config = tmp_path / "baseline-warden.toml"
    config.write_text(
        """
[policy]
required_status = "newly_or_widely"
unknown_behavior = "warn"

[include]
paths = ["unmatched/**"]

[ignore]
globs = []

[output]
formats = ["console"]
"""
    )

    lock_path = tmp_path / "baseline.lock.json"
    write_lock(lock_path, BaselineLock())

    runner = CliRunner()
    cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        result = runner.invoke(
            app,
            [
                "scan",
                "--config",
                str(config),
                "--lock-path",
                str(lock_path),
                "--paths",
                "core/templates/**/*.html",
                "--paths",
                "core/static/**/*.css",
                "--summary-only",
                "--dry-run",
            ],
            catch_exceptions=False,
        )
    finally:
        os.chdir(cwd)

    assert result.exit_code == 0
    assert "Total:" in result.stdout

