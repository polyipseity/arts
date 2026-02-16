# Content organisation

This repository is a compact Python toolkit — keep structure predictable and tests authoritative.

Recommended layout

- `README.md` — short project description
- `pyproject.toml` — authoritative configuration (tests, linters)
- `scripts/` — small helper scripts (executable utilities)
- `tests/` — pytest tests (must mirror behavior of production code)
- `.venv/`, `.github/`, config files — environment & CI helpers

Naming & placement

- New library modules: prefer `src/` if adding a library package; otherwise place single-file scripts in `scripts/` and add tests under `tests/`.
- Tests: `tests/test_*.py`
- Documentation: keep short README; use `rumdl` rules for Markdown formatting.

Metadata & typing

- Use `pyproject.toml` for dependency and tool configuration.
- Type-checking must pass with `pyright` (project is configured `strict`).
