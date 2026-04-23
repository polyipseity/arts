# AGENTS — arts (sub-repository)

A small, self-contained Python collection of tools/tests focused on strict documentation, type-safety and lightweight utilities.

## Quick reference

- Project root: repository root (current workspace)
- Primary entrypoints: `pyproject.toml`, `README.md`, `tests/`
- Test runner: `pytest` (see `tests/`)
- Linters / checks: `ruff`, `ty`, `rumdl` (Markdown)
- Python requirement: **3.14+** (see `pyproject.toml`)

## Safe startup (quick)

1. Create + activate a virtual environment
   - PowerShell: `uv venv && .\.venv\Scripts\Activate.ps1`
   - POSIX: `uv venv && source .venv/bin/activate`
2. Install project and dev tools (use your environment manager):
   - Example: `uv run -m pip install -e .[dev]` (or follow your org's workflow)
3. Run tests: `uv run -m pytest`
4. Run type and lint checks: `uv run --locked ty check`, `ruff check .`, `uv run rumdl check .`

## What to expect in this repo

- `tests/` — unit & meta-tests (see `test_docstrings.py` which enforces docstring coverage)
- `scripts/` — utility scripts
- `pyproject.toml` — authoritative configuration for tests, linters, and dev deps

## Test standard (ledger-style)

- Preserve top-level policy tests (`tests/test_module_exports.py`, `tests/test_docstrings.py`).
- Keep shared fixture wiring in `tests/conftest.py` with AnyIO backend and `pytest_plugins`.
- Keep typed reusable helpers in `tests/utils.py`.
- Mirror source layout for behavior tests where practical (`tests/scripts_/`).
- Ensure test modules include module docstrings and `__all__ = ()`.
- For each behavior change, cover both happy path and failure path.

## Developer & agent guidelines

- All code changes must keep tests green locally before opening PRs. ✅
- The test suite enforces module-level and exported-symbol docstrings — preserve and add docstrings for new public APIs. 🔧
- Run `ty` and `ruff` for type and style checks; run `rumdl` for Markdown linting.
- Ask the repository owner before modifying packaging, CI/workflows, or external release scripts.

---

## Project architecture & quick patterns

- Purpose: small utilities + helper scripts to manage artwork stored in `arts/` as chunked `.xcf.*` files.
- Code layout: logic lives in `scripts/`; tests live in `tests/`; there is no `src/` package currently.
- Public-surface rules: every module must declare `__all__` as a `tuple[str, ...]` and include a module-level docstring; exported functions/classes must have docstrings (see `tests/test_module_exports.py` and `tests/test_docstrings.py`).
- Type & linting: `ty` enforces strict diagnostics via `[tool.ty.rules]`; `ruff` enforces style (line-length 88); `rumdl` formats Markdown.
- Packaging note: `pyproject.toml` uses `uv_build` with an empty `module-name` (this project is not packaged as a library). Do not add packages to the build backend without approval.

## Critical workflows (commands)

- Setup: `uv venv && .\\.venv\\Scripts\\Activate.ps1`
- Install: `uv run -m pip install -e .[dev]`
- Tests: `uv run -m pytest` (defaults in `pyproject.toml` set coverage and parallel options)
- Lint/type: `ruff check . --fix`, `uv run --locked ty check`, `uv run rumdl check .`
- Asset handling: use `scripts/split.py` and `scripts/unsplit.py` for chunked files in `arts/` — do not manually recombine or add binary chunks without coordination.

## Agent-specific rules & guardrails

- Always propose a `Conventional Commit` message and list of changed files before committing.
- Preserve module docstrings and `__all__` semantics; place `__all__` after top-level imports and keep it a tuple of string constants.
- Add or update tests for any behavioral change — tests are the authoritative source of truth.
- Do not change `pyproject.toml` version, `tool.uv.build-backend.module-name`, or CI/workflows without explicit maintainers' approval.
- For changes touching large binary assets under `arts/`, confirm approach with the repository owner and prefer `scripts/` utilities.

## Example agent PR checklist

1. Run `pytest`, `ty`, `ruff`, and `rumdl` locally. Fix any failures.
2. Add tests for the change and ensure docstrings/`__all__` are updated.
3. Provide a one-line Conventional Commit message and a short PR description listing changed files and test results.

---

For operational details and quickstart steps see the `.agents/instructions/` files.
