# Contributing to baseline-warden

Thanks for your interest in improving Baseline Warden! This guide covers local development, testing, and how to propose changes.

## Developer setup

```bash
# Requirements: Python 3.11+ and uv (e.g., `pipx install uv`)
uv venv .venv && source .venv/bin/activate
uv sync --all-extras  # installs dev extras (pytest)

# Build a local Baseline snapshot (fetches data)
bw sync --lock

# Run the tests
pytest

# Try the CLI on a project
bw scan --out console --summary-only
```

## Project layout

- `baseline_warden/`
  - `cli.py` — Typer CLI (`bw sync`, `bw scan`)
  - `config.py` — Pydantic models for `baseline-warden.toml`
  - `index/` — data fetch/build/cache for Web Status + web-features
  - `detect/` — HTML & CSS detectors + file walker
  - `evaluate/` — mapping + policy evaluation
  - `outputs/` — console table, JSON, and GitHub annotations
- `docs/CONFIG.md` — detailed user configuration guide
- `.github/workflows/` — CI that runs a full scan

## Workflow

1. Keep changes focused; write or update tests for behavior changes.
2. Run `pytest` locally; ensure green.
3. Open a PR with a clear description and examples (screenshots or output when helpful).

## Testing

- Unit tests live in `tests/`; they run quickly and do not require network.
- When you change behavior (detectors, policy, outputs), add a small, targeted test near the change.

## Style & dependencies

- Python 3.11+ with type hints; follow the existing style and keep diffs minimal.
- Avoid adding new runtime dependencies unless necessary.

## Questions

- Usage/configuration: see the Configuration guide: [docs/CONFIG.md](docs/CONFIG.md).
- Not sure about an approach? Open a discussion or a draft PR to gather feedback early.
