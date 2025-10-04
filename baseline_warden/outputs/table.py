"""Console table output for Baseline findings."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from rich.console import Console
from rich.table import Table

from ..evaluate.policy import EvaluationSummary, Finding

SEVERITY_EMOJI = {"error": "❌", "warning": "⚠️", "info": "✅"}


def render_console(
    findings: Iterable[Finding],
    summary: EvaluationSummary,
    *,
    root: Path,
    summary_only: bool = False,
) -> None:
    console = Console()
    if not summary_only:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Severity", justify="center")
        table.add_column("Status")
        table.add_column("Feature")
        table.add_column("BCD Key")
        table.add_column("Location")
        table.add_column("Message")

        for finding in findings:
            location = f"{finding.detection.path}:{finding.detection.line}"
            if finding.severity == "info" and finding.allowlisted:
                message = f"{finding.message} (allowlisted)"
            else:
                message = finding.message
            feature_title = finding.feature.title if finding.feature else "<unknown>"
            table.add_row(
                SEVERITY_EMOJI.get(finding.severity, ""),
                finding.status,
                feature_title,
                finding.detection.bcd_key,
                location,
                message,
            )
        console.print(table)

    console.print(
        f"Total: {summary.total} • Failures: {summary.outcomes.get('fail', 0)} • "
        f"Warnings: {summary.outcomes.get('warn', 0)} • Passes: {summary.outcomes.get('pass', 0)}"
    )
    console.print(
        f"Statuses: widely={summary.statuses.get('widely', 0)}, newly={summary.statuses.get('newly', 0)}, "
        f"limited={summary.statuses.get('limited', 0)}, unknown={summary.statuses.get('unknown', 0)}"
    )
