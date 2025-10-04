from pathlib import Path

from baseline_warden.detect.css import detect_css


def test_ignores_font_face_descriptors(tmp_path: Path) -> None:
    css = """
    @font-face {
      font-family: 'Test';
      src: url(test.woff2) format('woff2'), local('Test');
      size-adjust: 105%;
    }
    """
    p = tmp_path / "font.css"
    p.write_text(css)
    keys = {d.bcd_key for d in detect_css(p)}
    assert "css.at-rules.font-face" in keys
    assert not any(k.startswith("css.properties.src") for k in keys)
    assert "css.properties.size-adjust" not in keys


def test_ignores_counter_style_descriptors(tmp_path: Path) -> None:
    css = """
    @counter-style bullets {
      system: cyclic;
      symbols: '*';
      suffix: ' ';
    }
    """
    p = tmp_path / "counter.css"
    p.write_text(css)
    keys = {d.bcd_key for d in detect_css(p)}
    assert "css.at-rules.counter-style" in keys
    assert "css.properties.system" not in keys
    assert "css.properties.symbols" not in keys
    assert "css.properties.suffix" not in keys


def test_ignores_page_descriptors_and_margin_at_rules(tmp_path: Path) -> None:
    css = """
    @page {
      size: A4 landscape;
    }
    @top-left { content: 'x'; }
    @bottom-right { content: 'y'; }
    """
    p = tmp_path / "page.css"
    p.write_text(css)
    keys = {d.bcd_key for d in detect_css(p)}
    assert "css.at-rules.page" in keys
    assert not any(k.startswith("css.properties.size") for k in keys)
    assert "css.at-rules.top-left" not in keys
    assert "css.at-rules.bottom-right" not in keys

