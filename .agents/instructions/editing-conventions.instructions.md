# Editing conventions

Short rules to keep the codebase consistent.

- Docstrings: every module and every exported function/class must have a non-empty docstring (enforced by `tests/test_docstrings.py`).
- Typing: prefer PEP 585 generics (e.g. `list[str]`) and keep `pyright` clean in `strict` mode.
- Formatting & linting: use `ruff` for Python and `rumdl` for Markdown.
- Tests: add or update tests for any behavior change; tests are the primary guardrail.

Good PRs

- Small, test-backed changes
- Green CI (`pytest`, `pyright`, `ruff`, `rumdl`)
- Clear commit message and short PR description
