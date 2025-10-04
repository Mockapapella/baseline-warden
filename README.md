# baseline-warden

Pre-commit/CI guardrail for Baseline support in HTML/CSS. Scans your code, maps features to Web Baseline (Web Status + MDN BCD), and flags anything not widely/newly available.

## Quick start

Install uv (one-liner):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install Baseline Warden from GitHub (master) into a project venv:

```bash
uv venv .venv && source .venv/bin/activate
uv pip install "git+https://github.com/Mockapapella/baseline-warden@master"

# Build a Baseline snapshot and scan
bw sync --lock
bw scan --out console,json  # fails on limited, warns on unknown
```

Tip: add `--summary-only` for compact console output.

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
            python-version: "3.11"

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



### Console summary-only mode

If you want a compact console output (especially in pre-commit), use:

```
bw scan --summary-only --out console
```

This prints totals and status counts without the per-finding table. The pre-commit hook in this repo uses `--summary-only` by default.

## Configuration reference

Create `baseline-warden.toml` at your repo root to tailor scanning:

```
[policy]
# Accept widely or newly (default); or set to "widely" to warn on newly.
required_status = "newly_or_widely"  # default
# How to handle unmapped tokens: "warn" (default) | "fail" | "ignore"
unknown_behavior = "warn"

[include]
# Globs to search; only HTML/Jinja/CSS files are considered by detectors.
# Defaults: "**/templates/**", "**/static/**", "templates/**", "static/**", "src/**"
paths = ["**/templates/**", "**/static/**"]

[ignore]
# Globs to skip (in addition to built-ins).
# Built-ins: node_modules/**, dist/**, build/**, vendor/**, coverage/**,
#            .next/**, .vite/**, .output/**, staticfiles/**, **/*.min.*
globs = ["staticfiles/**"]

[allowlist]
# Always pass specific features or BCD keys, regardless of status
feature_ids = ["accent-color"]
bcd_keys    = ["css.properties.margin-inline.auto"]

[output]
# One or more of: console, json, gh-annotations
formats = ["console", "json"]
```

CLI overrides:
- `bw scan --paths <glob> [--paths <glob> ...]` limits the scan without changing config.
- `bw scan --summary-only` shows totals without the table.
- `bw sync --refresh` bypasses caches when building the lock snapshot.

Minimal usage (no config):
- Defaults scan common web folders recursively (`**/templates/**`, `**/static/**`) and skip typical vendor/build folders.
- For projects that nest source under a subfolder (monorepos, services), pass `--paths` to scope the scan without editing config.

### Examples across frameworks

- Static sites / docs tools (pure HTML + CSS):
  - `bw scan --paths "**/*.html" --paths "assets/**/*.css"`
- Jinja templating in any stack (Python, Go, Rust, Node):
  - `bw scan --paths "**/templates/**/*.html" --paths "**/templates/**/*.{jinja,jinja2}" --paths "**/static/**/*.css"`
- Server frameworks with conventional templates/static (e.g., Flask, Django, Rails-equivalents using HTML templates):
  - `bw scan --paths "**/templates/**/*.html" --paths "**/static/**/*.css"`
- Node/monorepos where you only want to scan CSS (global styles, CSS Modules, Tailwind output):
  - `bw scan --paths "**/*.css"`

These are just examples; adjust globs to your layout. The scanner is framework/language agnostic—it only reads HTML/Jinja/CSS files wherever they live.
