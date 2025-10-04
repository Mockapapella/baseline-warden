from pathlib import Path

from baseline_warden.config import BaselineWardenConfig
from baseline_warden.detect import collect_detections


def test_collect_detections_scans_html_and_css(tmp_path: Path) -> None:
    (tmp_path / "templates").mkdir()
    (tmp_path / "static").mkdir()

    html_file = tmp_path / "templates" / "index.html"
    html_file.write_text("<dialog popover>Test</dialog>")

    css_file = tmp_path / "static" / "style.css"
    css_file.write_text("button:focus-visible { position: sticky; }")

    config = BaselineWardenConfig()
    config.include.paths = ["templates/**/*.html", "static/**/*.css"]

    detections = collect_detections(tmp_path, config)
    keys = {d.bcd_key for d in detections}

    assert "html.elements.dialog" in keys
    assert "html.elements.dialog.popover" in keys
    assert "css.selectors.focus-visible" in keys
    assert "css.properties.position.sticky" in keys
