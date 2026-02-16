# Core workflows

Commands you will use frequently.

- Run the test suite (recommended):

  ```bash
  uv run -m pytest
  ```

- Run linters / type checks:

  ```bash
  ruff check .
  pyright
  rumdl .
  ```

- Add a test for every bug fix or new feature. The repository's `pytest.ini` (via `pyproject.toml`) sets `--cov` and other defaults.

Notes

- `test_docstrings.py` enforces module-level and exported-symbol docstrings — update tests when APIs change.
- Keep commits small and focused; include tests and changelog notes where appropriate.
