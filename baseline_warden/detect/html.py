"""HTML template detector emitting Baseline-compatible BCD keys."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, List, Sequence

from .common import Detection


class _BaselineHTMLParser(HTMLParser):
    """HTML parser that records elements and attributes encountered."""

    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self._path = path
        self.detections: List[Detection] = []

    def handle_starttag(self, tag: str, attrs: Sequence[tuple[str, str | None]]) -> None:  # type: ignore[override]
        line, _ = self.getpos()
        tag_key = f"html.elements.{tag}"
        self.detections.append(Detection(path=self._path, line=line, bcd_key=tag_key))

        for attr, _ in attrs:
            if not attr:
                continue
            key = attr.lower()
            if key.startswith("data-") or key.startswith("x-") or key.startswith("on"):
                continue
            attr_key = f"html.elements.{tag}.{key}"
            self.detections.append(Detection(path=self._path, line=line, bcd_key=attr_key))

    def handle_startendtag(self, tag: str, attrs: Sequence[tuple[str, str | None]]) -> None:  # type: ignore[override]
        self.handle_starttag(tag, attrs)


def detect_html(path: Path, *, encoding: str = "utf-8") -> List[Detection]:
    """Detect HTML elements and attributes mapping to BCD keys."""

    try:
        text = path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        text = path.read_text(encoding=encoding, errors="ignore")

    parser = _BaselineHTMLParser(path)
    parser.feed(text)
    parser.close()
    return parser.detections


__all__ = ["detect_html"]
