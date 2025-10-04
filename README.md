# baseline-warden

Baseline Warden enforces Baseline compatibility for HTML and CSS assets by mapping parsed tokens to official Web Status Baseline data and the `web-features` dataset.

## What it does today

- `bw sync --lock` downloads Baseline data (Web Status API + `web-features`), writes `baseline.lock.json`, and records SHA-256 hashes for reproducible CI runs.
- `bw scan` walks configured HTML/CSS paths, emits BCD keys, resolves them against the lock snapshot, and evaluates policy:
  - Fails on `limited` features.
  - Passes on `widely`; passes/warns on `newly` depending on policy (`widely` vs `newly_or_widely`).
  - Warns/fails/ignores `unknown` per configuration.
- Outputs include:
  - Rich console table summarising severity, Baseline status, feature name, and file locations.
  - `report.json` for CI artifacts.
  - GitHub Actions annotations (up to 50) for PR feedback.

## Quick start

```bash
uv venv .venv
source .venv/bin/activate
uv sync --all-extras  # install baseline-warden + dev extras

# Fetch Baseline data and snapshot into baseline.lock.json
bw sync --lock

# Scan configured paths (fails on limited features)
bw scan --out console,json

# Dry run to preview without failing the build
bw scan --dry-run
```

Configuration defaults live in `baseline-warden.toml`. Use `--config` and `--lock-path` to point at alternative locations.

## License

MIT
