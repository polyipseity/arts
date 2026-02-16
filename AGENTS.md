# AGENTS — arts (sub-repository)

A small, self-contained Python collection of tools/tests focused on strict documentation, type-safety and lightweight utilities.

## Quick reference

- Project root: repository root (current workspace)
- Primary entrypoints: `pyproject.toml`, `README.md`, `tests/`
- Test runner: `pytest` (see `tests/`)
- Linters / checks: `ruff`, `pyright`, `rumdl` (Markdown)
- Python requirement: **3.12+** (see `pyproject.toml`)"

## Safe startup (quick)

1. Create + activate a virtual environment
   - PowerShell: `python -m venv .venv && .\.venv\Scripts\Activate.ps1`
   - POSIX: `python -m venv .venv && source .venv/bin/activate`
2. Install project and dev tools (use your environment manager):
   - Example: `python -m pip install -e .[dev]` (or follow your org's workflow)
3. Run tests: `python -m pytest`
4. Run type and lint checks: `pyright`, `ruff check .`, `rumdl .`

## What to expect in this repo

- `tests/` — unit & meta-tests (see `test_docstrings.py` which enforces docstring coverage)
- `scripts/` — utility scripts
- `pyproject.toml` — authoritative configuration for tests, linters, and dev deps

## Developer & agent guidelines

- All code changes must keep tests green locally before opening PRs. ✅
- The test suite enforces module-level and exported-symbol docstrings — preserve and add docstrings for new public APIs. 🔧
- Run `pyright` and `ruff` for type and style checks; run `rumdl` for Markdown linting.
- Ask the repository owner before modifying packaging, CI/workflows, or external release scripts.

---

For detailed agent-facing instructions see the files in `.github/instructions/` (quickstart, workflows, editing, testing, commit conventions).
