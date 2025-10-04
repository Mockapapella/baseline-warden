"""Detection orchestration for Baseline Warden."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

from ..config import BaselineWardenConfig
from .common import Detection, iter_included_files
from .css import detect_css
from .html import detect_html

HTML_EXTENSIONS = {".html", ".htm", ".jinja", ".jinja2"}
CSS_EXTENSIONS = {".css"}


def collect_detections(root: Path, config: BaselineWardenConfig) -> List[Detection]:
    """Collect detections for configured include paths and file types."""

    detections: List[Detection] = []
    include_patterns = config.include.paths
    ignore_patterns = config.ignore.globs

    def _relative(path: Path) -> Path:
        try:
            return path.relative_to(root)
        except ValueError:
            return path

    html_files = iter_included_files(
        root,
        include_patterns=include_patterns,
        ignore_patterns=ignore_patterns,
        extensions=HTML_EXTENSIONS,
    )
    for file_path in html_files:
        relative = _relative(file_path)
        for detection in detect_html(file_path):
            detections.append(
                Detection(
                    path=relative,
                    line=detection.line,
                    bcd_key=detection.bcd_key,
                    detail=detection.detail,
                )
            )

    css_files = iter_included_files(
        root,
        include_patterns=include_patterns,
        ignore_patterns=ignore_patterns,
        extensions=CSS_EXTENSIONS,
    )
    for file_path in css_files:
        relative = _relative(file_path)
        for detection in detect_css(file_path):
            detections.append(
                Detection(
                    path=relative,
                    line=detection.line,
                    bcd_key=detection.bcd_key,
                    detail=detection.detail,
                )
            )

    return detections


__all__ = ["collect_detections", "Detection"]
