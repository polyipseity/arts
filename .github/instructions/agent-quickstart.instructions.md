# Agent quickstart

A minimal checklist to get productive in this sub-repository.

1. Environment
   - Create & activate a venv (see `AGENTS.md`).
   - Use the project's Python (3.12+).

2. Install developer tools
   - Install project and dev dependencies (example): `uv run -m pip install -e .[dev]`.
   - Alternatively use your org's environment manager (poetry/uv/venv).

3. First commands (safe)
   - `uv run -m pytest`            # run tests
   - `ruff check . --fix` # format & lint fixes
   - `pyright`                    # static type check
   - `rumdl .`                    # markdown lint/format

4. When making changes
   - Run the tests and linters locally before committing.
   - Add or update tests for any behavioral change.
   - Preserve module- and API-level docstrings (tests enforce this).

5. When in doubt
   - Ask a short clarifying question before making non-trivial edits.

Agent responsibilities (for automated agents)

- Present a single, proposed `Conventional Commit` message and the list of changed files before creating any commit.
- Ensure any new/changed public symbols have docstrings and that `__all__` is updated (tuple of strings placed after imports).
- Add or update tests for behavior changes; do not leave failing tests.
- Do not modify package metadata (`pyproject.toml`), CI/workflow files, or large binary assets in `arts/` without human approval.
