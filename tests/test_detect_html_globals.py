from pathlib import Path

from baseline_warden.detect.html import detect_html


def test_ignores_common_global_and_aria_attributes(tmp_path: Path) -> None:
    html = '<button id="x" class="y" aria-label="z">Click</button>'
    p = tmp_path / "globals.html"
    p.write_text(html)

    keys = {d.bcd_key for d in detect_html(p)}
    assert "html.elements.button" in keys
    assert "html.elements.button.id" not in keys
    assert "html.elements.button.class" not in keys
    assert "html.elements.button.aria-label" not in keys

