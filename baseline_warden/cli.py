"""Typer-based CLI entry point for Baseline Warden."""

from __future__ import annotations

from pathlib import Path
from typing import List

import typer

import httpx

from .config import BaselineWardenConfig, load_config
from .index.build import (
    assemble_lock_features,
    build_web_features_index,
    fetch_web_features_dataset,
)
from .index.cache import BaselineLock, get_cache_dir, load_lock, write_lock
from .index.fetch import fetch_features

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
        dataset = fetch_web_features_dataset(cache_path=web_features_cache)
        index = build_web_features_index(dataset)
        baseline_result = fetch_features(cache_path=baseline_cache)
    except httpx.HTTPError as exc:  # pragma: no cover - network failure
        raise typer.Exit(code=1, message=f"Failed to fetch Baseline data: {exc}")

    lock_entries = assemble_lock_features(index=index, baseline_features=baseline_result.features)
    snapshot = BaselineLock(features=lock_entries)
    write_lock(out_path, snapshot)

    typer.echo(
        "Created Baseline lock file at "
        f"{out_path} ({snapshot.feature_count} features; generated_at={snapshot.generated_at.isoformat()})"
    )


@app.command()
def scan(
    config: Path = typer.Option(DEFAULT_CONFIG_PATH, "--config", help="Path to baseline-warden.toml."),
    out: List[str] = typer.Option(["console"], "--out", help="Output formats to emit."),
    ci: bool = typer.Option(False, "--ci", help="Enable CI-friendly behavior (non-zero exit on limited features)."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Run detectors without policy enforcement."),
    lock_path: Path = typer.Option(
        DEFAULT_LOCK_PATH,
        "--lock-path",
        help="Path to baseline.lock.json produced by `bw sync --lock`.",
    ),
) -> None:
    """Scan configured paths for non-Baseline features (stub)."""

    cfg = _load_config(config)
    if not lock_path.exists():
        typer.echo(
            "Lock file not found. Run `bw sync --lock` before scanning or pass --lock-path.",
            err=True,
        )
        raise typer.Exit(code=2)

    lock = load_lock(lock_path)
    typer.echo("Baseline Warden MVP scaffold")
    typer.echo(f" Policy: required_status={cfg.policy.required_status}, unknown_behavior={cfg.policy.unknown_behavior}")
    typer.echo(f" Include paths: {', '.join(cfg.include.paths)}")
    typer.echo(f" Ignore globs: {', '.join(cfg.ignore.globs[:4])} ...")
    typer.echo(f" Outputs requested: {', '.join(out)}")
    typer.echo(
        " Lock snapshot: "
        f"{lock.feature_count} features (generated_at={lock.generated_at.isoformat()})"
    )

    if dry_run:
        typer.echo(" Dry run complete (no detections performed yet).")
        raise typer.Exit(code=0)

    typer.echo(" Detection logic not implemented yet; exiting with success for MVP skeleton.")
    if ci:
        typer.echo(" CI mode requested; returning success until detectors are implemented.")
    raise typer.Exit(code=0)


if __name__ == "__main__":  # pragma: no cover
    app()
