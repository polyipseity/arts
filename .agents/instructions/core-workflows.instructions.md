# Core workflows

Commands you will use frequently.

- Run the test suite (recommended):

  ```bash
  uv run -m pytest
  ```

- Run focused tests for scripts mirrored under `tests/scripts_/` first:

  ```bash
  uv run -m pytest tests/scripts_/test_split.py tests/scripts_/test_unsplit.py
  ```

- Run helper/policy tests when touching fixture or meta-test logic:

  ```bash
  uv run -m pytest tests/tests/test_utils.py tests/test_module_exports.py tests/test_docstrings.py
  ```

  When covering asynchronous behaviour, decorate tests with `@pytest.mark.anyio` and rely on AnyIO/Asyncer helpers.

- Run linters / type checks:

  ```bash
  ruff check .
  uv run --locked ty check
  uv run rumdl check .
  ```

- Add a test for every bug fix or new feature. The repository's `pytest.ini` (via `pyproject.toml`) sets `--cov` and other defaults.

- Preferred verification order for changes:
  1. Targeted tests for touched modules.
  2. Full `pytest`.
  3. `uv run --locked ty check`.
  4. `ruff check .`.
  5. `uv run rumdl check .`.

Notes

- `test_docstrings.py` enforces module-level and exported-symbol docstrings — update tests when APIs change.
- Keep commits small and focused; include tests and changelog notes where appropriate.
- Keep test coverage robust: include both happy-path and failure-path scenarios.
