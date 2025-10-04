from pathlib import Path

from typer.testing import CliRunner

from baseline_warden.cli import app
from baseline_warden.index.cache import BaselineLock, LockFeature, write_lock


def test_summary_only_hides_table(tmp_path: Path) -> None:
    # Prepare minimal project
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "index.html").write_text("<p>ok</p>")

    # Config
    config = tmp_path / "baseline-warden.toml"
    config.write_text(
        """
[policy]
required_status = "newly_or_widely"
unknown_behavior = "warn"

[include]
paths = ["templates/**/*.html"]

[ignore]
globs = []

[output]
formats = ["console"]
"""
    )

    # Empty lock is fine; detections map to unknown and we only check output structure
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
                "--summary-only",
                "--dry-run",
            ],
            catch_exceptions=False,
        )
    finally:
        os.chdir(cwd)

    assert result.exit_code == 0
    out = result.stdout
    assert "Total:" in out and "Statuses:" in out
    assert "Severity" not in out  # table header suppressed

