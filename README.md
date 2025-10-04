# baseline-warden

Minimal scaffolding for the Baseline Warden MVP. The project enforces Baseline compatibility for HTML and CSS assets by mapping parsed tokens to the Web Platform Dashboard Baseline data.

## Current status

This is an initial skeleton:

- CLI entry point stubbed with Typer commands (`bw sync`, `bw scan`).
- Configuration model capturing agreed policy defaults.
- Package layout for index, detection, evaluation, and output modules.
- Pre-commit hook snippet and GitHub Action workflow placeholders.

Implementation work still required: feature indexing, file detectors, policy evaluation, and report generation.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
bw --help
```

Run `bw scan --dry-run` to confirm the CLI is wired (currently outputs a stub message).

## License

MIT
