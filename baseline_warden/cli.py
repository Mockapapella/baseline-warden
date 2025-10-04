"""Typer-based CLI entry point for Baseline Warden."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import typer

from .config import BaselineWardenConfig, load_config

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

    placeholder = {
        "version": 1,
        "note": "TODO: replace with fetched Baseline feature index.",
        "features": [],
    }
    out_path.write_text(json.dumps(placeholder, indent=2))
    typer.echo(f"Created placeholder lock file at {out_path}")


@app.command()
def scan(
    config: Path = typer.Option(DEFAULT_CONFIG_PATH, "--config", help="Path to baseline-warden.toml."),
    out: List[str] = typer.Option(["console"], "--out", help="Output formats to emit."),
    ci: bool = typer.Option(False, "--ci", help="Enable CI-friendly behavior (non-zero exit on limited features)."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Run detectors without policy enforcement."),
) -> None:
    """Scan configured paths for non-Baseline features (stub)."""

    cfg = _load_config(config)
    typer.echo("Baseline Warden MVP scaffold")
    typer.echo(f" Policy: required_status={cfg.policy.required_status}, unknown_behavior={cfg.policy.unknown_behavior}")
    typer.echo(f" Include paths: {', '.join(cfg.include.paths)}")
    typer.echo(f" Ignore globs: {', '.join(cfg.ignore.globs[:4])} ...")
    typer.echo(f" Outputs requested: {', '.join(out)}")

    if dry_run:
        typer.echo(" Dry run complete (no detections performed yet).")
        raise typer.Exit(code=0)

    typer.echo(" Detection logic not implemented yet; exiting with success for MVP skeleton.")
    if ci:
        typer.echo(" CI mode requested; returning success until detectors are implemented.")
    raise typer.Exit(code=0)


if __name__ == "__main__":  # pragma: no cover
    app()
