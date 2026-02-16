# Agent quickstart

A minimal checklist to get productive in this sub-repository.

1. Environment
   - Create & activate a venv (see `AGENTS.md`).
   - Use the project's Python (3.12+).

2. Install developer tools
   - Install project and dev dependencies (example): `python -m pip install -e .[dev]`.
   - Alternatively use your org's environment manager (poetry/uv/venv).

3. First commands (safe)
   - `python -m pytest`            # run tests
   - `ruff check . --fix` # format & lint fixes
   - `pyright`                    # static type check
   - `rumdl .`                    # markdown lint/format

4. When making changes
   - Run the tests and linters locally before committing.
   - Add or update tests for any behavioral change.
   - Preserve module- and API-level docstrings (tests enforce this).

5. When in doubt
   - Ask a short clarifying question before making non-trivial edits.
