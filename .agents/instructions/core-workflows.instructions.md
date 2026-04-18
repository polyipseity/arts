# Core workflows

Commands you will use frequently.

- Run the test suite (recommended):

  ```bash
  uv run -m pytest
  ```

  When covering asynchronous behaviour, decorate tests with `@pytest.mark.anyio` and rely on AnyIO/Asyncer helpers.

- Run linters / type checks:

  ```bash
  ruff check .
  uv run --locked ty check
  rumdl .
  ```

- Add a test for every bug fix or new feature. The repository's `pytest.ini` (via `pyproject.toml`) sets `--cov` and other defaults.

Notes

- `test_docstrings.py` enforces module-level and exported-symbol docstrings — update tests when APIs change.
- Keep commits small and focused; include tests and changelog notes where appropriate.
