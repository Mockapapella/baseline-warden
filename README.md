# baseline-warden

Pre-commit/CI gate for Baseline compatibility in HTML/CSS.

Uses Web Status + web-features (MDN BCD) to flag features that aren’t widely/newly available.

## Quick Start

```bash
uv venv .venv && source .venv/bin/activate
uv sync --all-extras
bw sync --lock
bw scan --out console,json    # fails on limited, warns on unknown
```

Console: `--summary-only` for compact output. Configuration guide: docs/CONFIG.md

## What It Checks

- Files: .html/.htm/.jinja/.jinja2 and .css (others ignored)
- Findings: Baseline status per BCD key (widely/newly/limited/unknown)
- Outputs: console (or summary-only), report.json, GitHub annotations

Noise control built-in: ignore global HTML attrs (class/id/aria-*), custom property declarations (`--foo`), descriptor-only at‑rules (@font-face/@counter-style/@page), and fall back value→property when needed.



### Console summary-only mode

If you want a compact console output (especially in pre-commit), use:

```
bw scan --summary-only --out console
```

This prints totals and status counts without the per-finding table. The pre-commit hook in this repo uses `--summary-only` by default.

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
