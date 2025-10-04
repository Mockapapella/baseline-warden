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

## Current scope

- Scans HTML, HTM, Jinja, and Jinja2 templates for element/attribute usage.
- Scans plain CSS files for properties, values, selectors (pseudo-classes/functions), and at-rules.
- Ignores CSS custom property declarations (e.g., `--token: ...`) and @property descriptors (`syntax`, `inherits`, `initial-value`); only the `@property` at-rule itself is reported.
- Ignores other asset types (JS/TS, JSX/TSX, Vue, Svelte, SCSS, etc.) for the MVP. These are possible future extensions.
- Default ignores include `node_modules`, build artifacts, and minified files; customize via `baseline-warden.toml`.

### Suppress noisy tokens

- HTML: common global attributes like `class`, `id`, `style`, `lang`, `title`, `dir`, `hidden`, and any `aria-*` are ignored during detection. Element-level features still appear (for example, `<dialog popover>` emits `html.elements.dialog` and `html.elements.dialog.popover`).
- CSS: custom property declarations (names beginning `--`) are ignored. Inside at-rules with descriptor taxonomies (`@property`, `@font-face`, `@counter-style`, `@page`), only the at-rule itself is reported; inner descriptors such as `src`, `system`, `size-adjust`, or `size` are not emitted as standalone properties.
- When a value-level key doesn’t map (for example, `css.properties.font-size.clamp`), Baseline Warden falls back to the base property (`css.properties.font-size`) to reduce false “unknown”s.

You can further suppress tokens using the allowlist in `baseline-warden.toml`:

```
[allowlist]
feature_ids = [
  # Always allow a feature by id
]
bcd_keys = [
  # Suppress specific BCD keys if they’re noisy in your project
  "css.properties.animation.infinite",
  "css.properties.margin-inline.auto",
]
```

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

These are just examples; adjust globs to your layout. The scanner doesn’t depend on Python or Django—it only reads HTML/Jinja/CSS files wherever they live.

For now, keep in mind:

- Only the file types above are parsed; non-matching files are skipped silently.
- HTML parsing is tolerant but not template-aware—Jinja/templating tags are ignored.
- CSS detection operates on raw CSS; preprocessors (SCSS/LESS) must emit CSS before scanning.
