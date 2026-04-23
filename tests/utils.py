"""Shared pytest fixtures and typed helpers for module-entrypoint tests.

This module centralizes test helpers that are reused across suites,
following the same pattern used by the ledger submodule.
"""

import runpy
import sys
from collections.abc import Callable
from typing import Any, Protocol

import asyncer
import pytest

"""Public symbols exported by this module."""
__all__ = ("RunModuleHelper", "run_module_helper")


class RunModuleHelper(Protocol):
    """Typed callable protocol for running a module as ``__main__`` in tests."""

    def __call__(self, module_name: str, argv: list[str]) -> dict[str, bool]:
        """Run ``module_name`` with ``argv`` and report whether runnify was called."""
        ...


@pytest.fixture
def run_module_helper(monkeypatch: pytest.MonkeyPatch) -> RunModuleHelper:
    """Return a helper that executes a module with patched ``asyncer.runnify``.

    The helper avoids actually running async entry points while still proving
    that the module-level ``__main__`` path calls ``asyncer.runnify``.
    """

    def run_module(module_name: str, argv: list[str]) -> dict[str, bool]:
        """Execute ``module_name`` via ``runpy`` with a fake ``runnify`` wrapper."""
        called: dict[str, bool] = {"ran": False}

        def fake_runnify(
            async_func: Callable[..., Any], *_args: object, **_kwargs: object
        ) -> Callable[..., Any]:
            """Mark the module as run and return a wrapper that closes coroutines."""
            called["ran"] = True

            def wrapper(*args: Any, **kwargs: Any) -> None:
                """Close the coroutine returned by ``async_func`` to avoid warnings."""
                try:
                    coro = async_func(*args, **kwargs)
                    coro.close()
                except Exception:
                    # Keep helper resilient: it is only used for smoke coverage.
                    pass

            return wrapper

        monkeypatch.setattr(asyncer, "runnify", fake_runnify)

        previous_argv = sys.argv[:]
        try:
            sys.argv[:] = argv
            for module in (module_name, "scripts"):
                sys.modules.pop(module, None)
            runpy.run_module(module_name, run_name="__main__")
        finally:
            sys.argv[:] = previous_argv

        return called

    return run_module
