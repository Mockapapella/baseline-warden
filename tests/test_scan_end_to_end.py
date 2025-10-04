import json
import os
from pathlib import Path

from typer.testing import CliRunner

from baseline_warden.cli import app
from baseline_warden.index.cache import BaselineLock, LockFeature, write_lock


def test_scan_detects_limited_feature(tmp_path: Path) -> None:
    (tmp_path / "templates").mkdir()
    (tmp_path / "static").mkdir()

    (tmp_path / "templates" / "index.html").write_text("<dialog>Test</dialog>")
    (tmp_path / "static" / "main.css").write_text("button { position: sticky; }")

    config = tmp_path / "baseline-warden.toml"
    config.write_text(
        """
[policy]
required_status = "newly_or_widely"
unknown_behavior = "warn"

[include]
paths = ["templates/**/*.html", "static/**/*.css"]

[ignore]
globs = []

[output]
formats = ["console", "json"]
"""
    )

    lock = BaselineLock(
        features=[
            LockFeature(
                feature_id="feature-dialog",
                title="Dialog",
                status="newly",
                bcd_keys=["html.elements.dialog"],
            ),
            LockFeature(
                feature_id="feature-sticky",
                title="position: sticky",
                status="limited",
                bcd_keys=["css.properties.position", "css.properties.position.sticky"],
            ),
        ]
    )
    lock_path = tmp_path / "baseline.lock.json"
    write_lock(lock_path, lock)

    runner = CliRunner()
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(
            app,
            ["scan", "--config", str(config), "--lock-path", str(lock_path)],
            catch_exceptions=False,
        )
    finally:
        os.chdir(cwd)

    assert result.exit_code == 1
    assert "Baseline violations detected" in result.output

    report_path = tmp_path / "report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text())
    status_counts = report["summary"]["statuses"]
    assert status_counts["limited"] >= 1
