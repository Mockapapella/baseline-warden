# Configuration Guide

This document covers Baseline Warden configuration in detail: available options, defaults, examples, and useful CLI overrides.

Baseline Warden reads `baseline-warden.toml` from the repository root by default. You can point elsewhere using `--config <path>`.

## File schema

```
[policy]
# Require baseline status. Choices: "widely" or "newly_or_widely" (default).
required_status = "newly_or_widely"

# How to treat unmapped tokens. Choices: "warn" (default), "fail", "ignore".
unknown_behavior = "warn"

[include]
# Search globs. Detectors only parse .html/.htm/.jinja/.jinja2/.css files.
# Defaults: "**/templates/**", "**/static/**", "templates/**", "static/**", "src/**"
paths = ["**/templates/**", "**/static/**"]

[ignore]
# Globs to skip. Built-ins are always applied:
# node_modules/**, dist/**, build/**, vendor/**, coverage/**,
# .next/**, .vite/**, .output/**, staticfiles/**, **/*.min.*
globs = []

[allowlist]
# Always pass these even if status would fail; or suppress noisy BCD keys.
feature_ids = []    # Example: ["accent-color"]
bcd_keys    = []    # Example: ["css.properties.margin-inline.auto"]

[output]
# Any of: console, json, gh-annotations
formats = ["console", "json"]
```

## Behavior details

- Policy and outcomes
  - limited → fail
  - widely → pass
  - newly → pass (or warn when `policy.required_status = "widely"`)
  - unknown → warn/fail/ignore according to `policy.unknown_behavior`
- Allowlist precedence
  - `allowlist.feature_ids` or `allowlist.bcd_keys` force a pass regardless of status
  - intended to suppress known noisy or acceptable usages

## What gets scanned

- Detectors only parse these extensions: `.html`, `.htm`, `.jinja`, `.jinja2`, `.css`.
- Files are discovered via `[include].paths` minus `[ignore].globs` and built-ins.
- CLI override without changing config: repeat `--paths` flags on the command line.

Examples:

```
bw scan --paths "**/*.html" --paths "assets/**/*.css"
bw scan --paths "app/templates/**/*.{html,jinja,jinja2}" --paths "app/static/**/*.css"
```

## Normalization (noise reduction)

- HTML: ignore global attributes `class`, `id`, `style`, `lang`, `title`, `dir`, `hidden`, and any `aria-*`.
- CSS: ignore custom property declarations (names starting `--`).
- At-rules with descriptors: only the at-rule is reported for `@property`, `@font-face`, `@counter-style`, `@page` (inner descriptors are not emitted as properties).
- Property value fallback: when `css.properties.<name>.<value>` doesn’t map, it falls back to `css.properties.<name>` when available.

## Outputs

- console: rich table of findings (or `--summary-only` for totals/status counts)
- json: writes `report.json` with a summary and structured findings
- gh-annotations: prints GitHub workflow commands for PR annotations (first 50)

## Locking and caches

- `bw sync --lock` builds `baseline.lock.json` from the Web Status API and the `web-features` dataset. The lock is deterministic for CI.
- Caches are stored under `~/.cache/baseline-warden/` by default.
- Environment override: set `BASELINE_WARDEN_CACHE_DIR` to change the cache path.
- `bw sync --refresh` refreshes the cached datasets before writing the lock.

## Examples

Minimal (defaults):

```
[policy]
required_status = "newly_or_widely"
unknown_behavior = "warn"

[output]
formats = ["console"]
```

Stricter policy (warn on newly, fail on unknown):

```
[policy]
required_status = "widely"
unknown_behavior = "fail"

[output]
formats = ["console", "json"]
```

Scoped scanning (monorepo, custom folders):

```
[include]
paths = ["services/web/templates/**", "services/web/static/**", "packages/site/**/*.css"]

[ignore]
globs = ["**/*.min.*", "**/vendor/**"]
```

Allowlist noisy items:

```
[allowlist]
feature_ids = ["accent-color"]
bcd_keys = ["css.properties.margin-inline.auto"]
```

## CI and pre-commit

Pre-commit (local):

```
- repo: local
  hooks:
    - id: baseline-warden
      name: baseline-warden
      entry: bw scan --dry-run --out console --summary-only --config baseline-warden.toml
      language: system
      files: '\\.(html|htm|jinja|jinja2|css)$'
```

GitHub Action (composite in this repo):

```
- uses: Mockapapella/baseline-warden/action@v0
  with:
    config: baseline-warden.toml
```

The included workflow `.github/workflows/baseline-warden.yml` runs `bw sync` + `bw scan --ci` and uploads `report.json`.

