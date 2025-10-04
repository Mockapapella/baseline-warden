"""Typer-based CLI entry point for Baseline Warden."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

import httpx

from .config import BaselineWardenConfig, load_config
from .index.build import (
    assemble_lock_features,
    build_web_features_index,
    fetch_web_features_dataset,
)
from .detect import collect_detections
from .evaluate.policy import evaluate_detections
from .evaluate.resolve import build_index
from .index.cache import BaselineLock, compute_sha256, get_cache_dir, load_lock, write_lock
from .index.fetch import fetch_features
from .outputs.gh_annotations import emit_annotations
from .outputs.json import write_json
from .outputs.table import render_console

app = typer.Typer(help="Baseline compatibility gate for web projects.")

DEFAULT_CONFIG_PATH = Path("baseline-warden.toml")
DEFAULT_LOCK_PATH = Path("baseline.lock.json")


def _load_config(path: Path) -> BaselineWardenConfig:
    if not path.exists():
        raise typer.Exit(code=2, message=f"Config not found: {path}")
    return load_config(path)


@app.command()
def sync(
    lock: bool = typer.Option(False, "--lock", help="Persist resolved Baseline data to baseline.lock.json."),
    out_path: Path = typer.Option(DEFAULT_LOCK_PATH, "--lock-path", help="Path to the lock snapshot."),
    refresh: bool = typer.Option(False, "--refresh", help="Ignore caches and refetch remote datasets."),
) -> None:
    """Fetch Baseline data and optionally persist a lock snapshot."""

    if not lock:
        typer.echo("Sync is stubbed in the MVP scaffold; use --lock to generate a placeholder lock file.")
        raise typer.Exit(code=0)

    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    web_features_cache = cache_dir / "web-features.json"
    baseline_cache = cache_dir / "webstatus-baseline.json"

    try:
        dataset = fetch_web_features_dataset(cache_path=web_features_cache, force_refresh=refresh)
        index = build_web_features_index(dataset)
        baseline_result = fetch_features(cache_path=baseline_cache, force_refresh=refresh)
    except httpx.HTTPError as exc:  # pragma: no cover - network failure
        raise typer.Exit(code=1, message=f"Failed to fetch Baseline data: {exc}")

    lock_entries = assemble_lock_features(index=index, baseline_features=baseline_result.features)
    lock_metadata = {
        "web_features": {
            "cache_path": str(web_features_cache),
            "sha256": compute_sha256(web_features_cache) if web_features_cache.exists() else None,
        },
        "web_status": {
            "cache_path": str(baseline_cache),
            "sha256": compute_sha256(baseline_cache) if baseline_cache.exists() else None,
            "total": baseline_result.total,
        },
    }
    snapshot = BaselineLock(features=lock_entries, metadata=lock_metadata)
    write_lock(out_path, snapshot)

    typer.echo(
        "Created Baseline lock file at "
        f"{out_path} ({snapshot.feature_count} features; generated_at={snapshot.generated_at.isoformat()})"
    )


@app.command()
def scan(
    config: Path = typer.Option(DEFAULT_CONFIG_PATH, "--config", help="Path to baseline-warden.toml."),
    out: Optional[List[str]] = typer.Option(None, "--out", help="Output formats to emit."),
    ci: bool = typer.Option(False, "--ci", help="Enable CI-friendly behavior (non-zero exit on limited features)."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Run detectors without policy enforcement."),
    summary_only: bool = typer.Option(False, "--summary-only", help="Show only summary lines for console output."),
    lock_path: Path = typer.Option(
        DEFAULT_LOCK_PATH,
        "--lock-path",
        help="Path to baseline.lock.json produced by `bw sync --lock`.",
    ),
) -> None:
    """Scan configured paths for non-Baseline features."""

    cfg = _load_config(config)
    if not lock_path.exists():
        typer.echo(
            "Lock file not found. Run `bw sync --lock` before scanning or pass --lock-path.",
            err=True,
        )
        raise typer.Exit(code=2)

    lock = load_lock(lock_path)
    formats = out or cfg.output.formats
    root = Path.cwd()

    detections = collect_detections(root, cfg)
    index = build_index(lock)
    findings, summary = evaluate_detections(index, detections, cfg)

    typer.echo(
        f"Policy required_status={cfg.policy.required_status}, unknown_behavior={cfg.policy.unknown_behavior}"
    )
    typer.echo(
        f"Scanned {len(detections)} detections across {len(formats)} output format(s)."
    )

    for fmt in formats:
        if fmt == "console":
            render_console(findings, summary, root=root, summary_only=summary_only)
        elif fmt == "json":
            report_path = Path("report.json")
            write_json(findings, summary, report_path)
            typer.echo(f" Wrote JSON report to {report_path}")
        elif fmt == "gh-annotations":
            emit_annotations(findings)
        else:
            typer.echo(f" Unknown output format '{fmt}' ignored.")

    if dry_run:
        typer.echo(" Dry run enabled; exiting without enforcing policy.")
        raise typer.Exit(code=0)

    if summary.has_failures():
        typer.echo(" Baseline violations detected.", err=True)
        raise typer.Exit(code=1)

    typer.echo(" Baseline scan passed.")
    raise typer.Exit(code=0)


if __name__ == "__main__":  # pragma: no cover
    app()
