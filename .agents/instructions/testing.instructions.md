# Testing

Testing conventions and how to run the suite.

- Test runner: `pytest` (configured via `pyproject.toml`).
- Test location: `tests/` — test files must follow `test_*.py` naming.
- Pytest defaults (from `pyproject.toml`): `--cov=./`, `--cov-report=term-missing`, `--dist=loadscope`, `-n=auto`.

Important checks

- `tests/test_docstrings.py` ensures:
  - Module-level docstrings exist.
  - Exported functions/classes (from `__all__`) have docstrings.
  - All top-level and nested defs contain docstrings.

Common commands

- Run full test suite:

  ```bash
  uv run -m pytest
  ```

- Run a single test file:

  ```bash
  uv run -m pytest tests/test_docstrings.py
  ```

- Run coverage report (already included in default `addopts`):

  ```bash
  uv run -m pytest
  ```

Guidelines

- Add tests for every bug fix or new feature.
- Keep tests deterministic and fast; prefer fixture-driven tests.
- When writing async tests, decorate with `@pytest.mark.anyio` and rely on AnyIO/Asyncer helpers rather than importing `asyncio` directly.
- Ensure type checks (`ty`) and linters (`ruff`) pass alongside tests.
