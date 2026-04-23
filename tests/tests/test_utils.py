"""Tests for shared helpers in :mod:`tests.utils`."""

import pytest

from ..utils import RunModuleHelper

"""Public symbols exported by this module (none)."""
__all__ = ()


def test_run_module_helper_marks_entrypoint_as_invoked(
    run_module_helper: RunModuleHelper,
) -> None:
    """Running a script module via helper should mark ``runnify`` as called."""
    called = run_module_helper("scripts.split", ["scripts.split"])
    assert called["ran"] is True


def test_run_module_helper_raises_for_missing_module(
    run_module_helper: RunModuleHelper,
) -> None:
    """Unknown modules should raise an import error from ``runpy``."""
    with pytest.raises(ImportError):
        run_module_helper("scripts.module_that_does_not_exist", ["missing"])
