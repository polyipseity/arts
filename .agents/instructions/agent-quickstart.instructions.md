# Agent quickstart

A minimal checklist to get productive in this sub-repository.

1. Environment
   - Create & activate a venv (see `AGENTS.md`).
   - Use the project's Python (3.14+).

2. Install developer tools
   - Install project and dev dependencies (example): `uv run -m pip install -e .[dev]`.
   - Alternatively use your org's environment manager (poetry/uv/venv).

3. First commands (safe)
   - `uv run -m pytest` # run tests
   - `ruff check . --fix` # format & lint fixes
   - `uv run --locked ty check` # static type check
   - `uv run rumdl check .` # markdown lint check

4. Testing-first workflow (required)
   - Mirror source layout in tests where practical:
     - `scripts/split.py` -> `tests/scripts_/test_split.py`
     - `scripts/unsplit.py` -> `tests/scripts_/test_unsplit.py`
   - Keep shared typed test helpers in `tests/utils.py`.
   - Keep AnyIO fixture wiring in `tests/conftest.py` and load shared fixtures via `pytest_plugins`.
   - Ensure each new test module includes:
     - module docstring
     - `__all__ = ()`
   - Cover both happy-path and failure-path behavior (not only parser smoke tests).

5. When making changes
   - Run the tests and linters locally before committing.
   - Add or update tests for any behavioral change.
   - Preserve module- and API-level docstrings (tests enforce this).

6. When in doubt
   - Ask a short clarifying question before making non-trivial edits.

Agent responsibilities (for automated agents)

- Present a single, proposed `Conventional Commit` message and the list of changed files before creating any commit.
- Ensure any new/changed public symbols have docstrings and that `__all__` is updated (tuple of strings placed after imports).
- Add or update tests for behavior changes; do not leave failing tests.
- Do not modify package metadata (`pyproject.toml`), CI/workflow files, or large binary assets in `arts/` without human approval.
- Prefer focused verification before full runs:
  - targeted tests for touched modules
  - full `pytest`
  - `ty`, `ruff`, `rumdl`
