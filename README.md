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

For now, keep in mind:

- Only the file types above are parsed; non-matching files are skipped silently.
- HTML parsing is tolerant but not template-aware—Jinja/templating tags are ignored.
- CSS detection operates on raw CSS; preprocessors (SCSS/LESS) must emit CSS before scanning.

## License

MIT
