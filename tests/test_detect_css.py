from pathlib import Path

from baseline_warden.detect.css import detect_css


def test_detect_css_emits_properties_values_and_selectors(tmp_path: Path) -> None:
    css = """
    @container style(size > 0) {
      .card { display: grid; }
    }
    button:focus-visible { position: sticky; }
    .menu:has(a[download]) { color: red; }
    """
    path = tmp_path / "sample.css"
    path.write_text(css.strip())

    detections = detect_css(path)
    keys = {d.bcd_key for d in detections}

    assert "css.at-rules.container" in keys
    assert "css.properties.display" in keys
    assert "css.properties.display.grid" in keys
    assert "css.selectors.focus-visible" in keys
    assert "css.selectors.has" in keys
    assert "css.properties.position.sticky" in keys
    assert "css.properties.color" in keys


def test_detect_css_handles_top_level_declarations(tmp_path: Path) -> None:
    css = "margin: auto;"
    path = tmp_path / "global.css"
    path.write_text(css)

    detections = detect_css(path)
    keys = {d.bcd_key for d in detections}

    assert "css.properties.margin" in keys
    assert "css.properties.margin.auto" in keys
