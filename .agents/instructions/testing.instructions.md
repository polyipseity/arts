# Testing

Testing is a first-class policy in this submodule. Mirror the structure and rigor
used in `self/ledger`.

## Baseline structure (required)

- Test runner: `pytest` (configured via `pyproject.toml`).
- Test location: `tests/` with files named `test_*.py`.
- Pytest defaults (from `pyproject.toml`):
  - `--cov=./`
  - `--cov-report=term-missing`
  - `--dist=loadscope`
  - `-n=auto`
  - `--strict-markers`
- Shared fixture wiring:
  - Keep AnyIO backend fixture in `tests/conftest.py`.
  - Load shared fixtures via `pytest_plugins = ("tests.utils",)`.
  - Keep reusable typed helpers in `tests/utils.py`.
- Mirror source layout where practical:
  - `scripts/*.py` → `tests/scripts_/test_*.py`
  - shared test helpers → `tests/tests/test_*.py`

## Policy tests (must remain green)

- `tests/test_module_exports.py`:
  - every Python module has top-level `__all__`
  - `__all__` must be a tuple of string constants
  - `__all__` must follow top-level imports
- `tests/test_docstrings.py`:
  - module-level docstrings
  - exported symbol docstrings
  - top-level and nested definition docstrings
- `tests/test_git_executable.py`:
  - script executable metadata validation

## Behavioral coverage expectations

For each touched script/module, add or update tests that cover:

1. Happy path behavior with realistic inputs.
2. Failure/error-prone branches (missing files, partial inputs, invalid states).
3. Parser/CLI adapter behavior (`parser()`, `invoke`, argument parsing).
4. Entrypoint smoke checks (`__main__` path) via shared helpers.
5. Multi-input or boundary behavior when applicable.

Do not replace robust checks with weaker assertions.

## Test module conventions

- Every test module must include a module docstring.
- Every test module must declare `__all__ = ()`.
- Prefer explicit types in tests and fixtures.
- Use `@pytest.mark.anyio` for async tests.
- Keep tests deterministic and file-system isolated (`tmp_path`).

## Concrete workflow

1. Run targeted tests for changed modules.
2. Run full suite.
3. Run lint/type checks.

Suggested command sequence:

```bash
uv run -m pytest tests/scripts_/test_split.py tests/scripts_/test_unsplit.py tests/tests/test_utils.py
uv run -m pytest
uv run --locked ty check
ruff check .
uv run rumdl check .
```

If a test fails, fix root cause first; do not delete or relax checks to pass.
