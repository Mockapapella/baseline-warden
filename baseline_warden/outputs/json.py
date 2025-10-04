"""JSON report output."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from ..evaluate.policy import EvaluationSummary, Finding


def write_json(findings: Iterable[Finding], summary: EvaluationSummary, path: Path) -> None:
    now = datetime.now(UTC).isoformat()
    data = {
        "version": "1",
        "generated_at": now,
        "summary": {
            "total": summary.total,
            "outcomes": summary.outcomes,
            "statuses": summary.statuses,
        },
        "findings": [
            {
                "file": str(finding.detection.path),
                "line": finding.detection.line,
                "bcd_key": finding.detection.bcd_key,
                "status": finding.status,
                "severity": finding.severity,
                "message": finding.message,
                "feature": {
                    "id": finding.feature.feature_id if finding.feature else None,
                    "title": finding.feature.title if finding.feature else None,
                },
                "allowlisted": finding.allowlisted,
            }
            for finding in findings
        ],
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
