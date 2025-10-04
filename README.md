# baseline-warden

Pre-commit/CI guardrail for Baseline support in HTML/CSS. Scans your code, maps features to Web Baseline (Web Status + MDN BCD), and flags anything not widely/newly available.

## Quick start

Install uv (one‑liner):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install Baseline Warden from GitHub (master) into a project venv and scan:

```bash
uv venv .venv && source .venv/bin/activate
uv pip install "git+https://github.com/Mockapapella/baseline-warden@master"

bw sync --lock                   # build a Baseline snapshot
bw scan --out console,json       # fails on limited; warns on unknown
# Tip: add --summary-only for compact console output
```

## What it checks

- Files: .html/.htm/.jinja/.jinja2 and .css (others ignored)
- Findings: Baseline status per BCD key (widely/newly/limited/unknown)
- Outputs: console (use `--summary-only` to keep it brief), `report.json`, GitHub annotations
- Noise control: ignores global HTML attrs (class/id/aria-*), custom property declarations (`--foo`), descriptor-only at‑rules (@font-face/@counter-style/@page); falls back value→property when helpful

## Integrations

- Pre-commit (blocking by default):
  ```yaml
  - repo: local
    hooks:
      - id: baseline-warden
        name: baseline-warden
        entry: bw scan --out console --summary-only --config baseline-warden.toml
        language: system
        files: '\\.(html|htm|jinja|jinja2|css)$'
  ```

- GitHub Actions (minimal working example):
  ```yaml
  name: Baseline Warden

  on:
    pull_request:
    push:
      branches:
        - main

  jobs:
    baseline:
      runs-on: ubuntu-latest
      steps:
        - name: Checkout
          uses: actions/checkout@v4

        - name: Set up Python
          uses: actions/setup-python@v5
          with:
            python-version: "3.13"

        - name: Install uv
          run: pip install uv

        - name: Sync dependencies
          run: uv sync --locked

        - name: Run Baseline scan
          run: uv run bw scan --out console --ci
  ```
  - Ensure `baseline.lock.json` is committed (recommended). If you prefer to build it in CI, add a step before the scan: `uv run bw sync --lock`.

## Configuration

Defaults usually “just work” for common layouts. For full options and examples, see the Configuration guide: [docs/CONFIG.md](docs/CONFIG.md).

## Contributing

See the contributing guide: [CONTRIBUTING.md](CONTRIBUTING.md) for developer setup and guidelines.
