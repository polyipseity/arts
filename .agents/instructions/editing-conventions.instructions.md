# Editing conventions

Short rules to keep the codebase consistent.

- Docstrings: every module and every exported function/class must have a non-empty docstring (enforced by `tests/test_docstrings.py`).
- Typing: prefer PEP 585 generics (e.g. `list[str]`) and keep `ty` clean with strict rules.
- Formatting & linting: use `ruff` for Python and `rumdl` for Markdown.
- Tests: add or update tests for any behavior change; tests are the primary guardrail.

Test file conventions

- Mirror source layout in tests where practical (`scripts/*.py` -> `tests/scripts_/test_*.py`).
- Every test module must have:
  - a module-level docstring
  - `__all__ = ()`
- Reusable typed test helpers belong in `tests/utils.py` and should be loaded via `tests/conftest.py`.
- Prefer explicit, branch-aware assertions covering both success and failure paths.

Good PRs

- Small, test-backed changes
- Green CI (`pytest`, `ty`, `ruff`, `rumdl`)
- Clear commit message and short PR description
