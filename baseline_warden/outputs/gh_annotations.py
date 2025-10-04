"""GitHub Actions workflow command output."""

from __future__ import annotations

from typing import Iterable

from ..evaluate.policy import Finding


def emit_annotations(findings: Iterable[Finding], *, limit: int = 50) -> None:
    count = 0
    for finding in findings:
        if finding.severity == "info":
            continue
        command = "::error" if finding.severity == "error" else "::warning"
        location = f"file={finding.detection.path},line={finding.detection.line}"
        message = finding.message
        if finding.feature:
            message = f"{finding.feature.title}: {message}"
        print(f"{command} {location}::{message}")
        count += 1
        if count >= limit:
            break
