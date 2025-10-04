from pathlib import Path

from baseline_warden.detect.html import detect_html


def test_detect_html_emits_element_and_attribute_keys(tmp_path: Path) -> None:
    html_content = """
    <html>
      <body>
        <dialog popover popovertarget="menu"></dialog>
        <a href="/about" download>About</a>
      </body>
    </html>
    """
    path = tmp_path / "sample.html"
    path.write_text(html_content.strip())

    detections = detect_html(path)
    keys = {d.bcd_key for d in detections}

    assert "html.elements.dialog" in keys
    assert "html.elements.dialog.popover" in keys
    assert "html.elements.dialog.popovertarget" in keys
    assert "html.elements.a" in keys
    assert "html.elements.a.href" in keys
    # 'download' attribute should be captured
    assert "html.elements.a.download" in keys


def test_detect_html_skips_data_and_event_attributes(tmp_path: Path) -> None:
    html_content = '<button data-test="foo" onclick="alert(\'hi\')">Click</button>'
    path = tmp_path / "skip.html"
    path.write_text(html_content)

    detections = detect_html(path)
    keys = {d.bcd_key for d in detections}

    assert "html.elements.button" in keys
    assert "html.elements.button.data-test" not in keys
    assert "html.elements.button.onclick" not in keys
