"""Behavior tests for :mod:`scripts.split`.

These tests mirror the source layout and cover both happy paths and
failure-prone branches.
"""

from os import PathLike

import pytest
from anyio import Path

from scripts import split

from ..utils import RunModuleHelper

"""Public symbols exported by this module (none)."""
__all__ = ()


def test_arguments_normalize_inputs_to_tuple_and_are_frozen() -> None:
    """``Arguments`` should normalize inputs to tuple and remain immutable."""
    args = split.Arguments(inputs=[Path("a"), Path("b")])
    assert isinstance(args.inputs, tuple)
    assert args.inputs == (Path("a"), Path("b"))
    assert split.Arguments.__dataclass_params__.frozen is True


@pytest.mark.anyio
async def test_main_splits_file_and_prunes_stale_chunks(
    tmp_path: PathLike[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Splitting writes expected chunks and removes stale trailing chunks."""
    source = Path(tmp_path) / "painting.xcf"
    await source.write_bytes(b"ABCDEFGHIJ")

    stale = Path(f"{source}.004")
    await stale.write_bytes(b"STALE")

    monkeypatch.setattr(split, "_SPLIT_SIZE", 4)
    await split.main(split.Arguments(inputs=[source]))

    assert await Path(f"{source}.001").read_bytes() == b"ABCD"
    assert await Path(f"{source}.002").read_bytes() == b"EFGH"
    assert await Path(f"{source}.003").read_bytes() == b"IJ"
    assert not await stale.exists()


@pytest.mark.anyio
async def test_main_empty_input_removes_previous_chunks(
    tmp_path: PathLike[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty files should produce no chunks and clean up old split parts."""
    source = Path(tmp_path) / "empty.xcf"
    await source.write_bytes(b"")

    old_chunk_1 = Path(f"{source}.001")
    old_chunk_2 = Path(f"{source}.002")
    await old_chunk_1.write_bytes(b"old")
    await old_chunk_2.write_bytes(b"old")

    monkeypatch.setattr(split, "_SPLIT_SIZE", 16)
    await split.main(split.Arguments(inputs=[source]))

    assert not await old_chunk_1.exists()
    assert not await old_chunk_2.exists()


@pytest.mark.anyio
async def test_main_processes_multiple_inputs(
    tmp_path: PathLike[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Multiple input files should be split independently in one call."""
    first = Path(tmp_path) / "first.xcf"
    second = Path(tmp_path) / "second.xcf"
    await first.write_bytes(b"ABCDE")
    await second.write_bytes(b"XYZ")

    monkeypatch.setattr(split, "_SPLIT_SIZE", 2)
    await split.main(split.Arguments(inputs=[first, second]))

    assert await Path(f"{first}.001").read_bytes() == b"AB"
    assert await Path(f"{first}.002").read_bytes() == b"CD"
    assert await Path(f"{first}.003").read_bytes() == b"E"
    assert await Path(f"{second}.001").read_bytes() == b"XY"
    assert await Path(f"{second}.002").read_bytes() == b"Z"


def test_parser_parses_inputs_as_anyio_paths() -> None:
    """CLI parser should convert positional inputs into ``anyio.Path`` objects."""
    ns = split.parser().parse_args(["a.xcf", "b.xcf"])
    assert len(ns.inputs) == 2
    assert all(isinstance(path, Path) for path in ns.inputs)


@pytest.mark.anyio
async def test_parser_invoke_resolves_paths_and_calls_main(
    tmp_path: PathLike[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Parser ``invoke`` should resolve inputs and forward normalized args to ``main``."""
    source = Path(tmp_path) / "resolved.xcf"
    await source.write_bytes(b"data")

    captured: dict[str, split.Arguments] = {}

    async def fake_main(args: split.Arguments) -> None:
        """Capture arguments supplied by parser invoke for assertions."""
        captured["args"] = args

    monkeypatch.setattr(split, "main", fake_main)

    ns = split.parser().parse_args([str(source)])
    await ns.invoke(ns)

    args = captured["args"]
    assert isinstance(args, split.Arguments)
    assert len(args.inputs) == 1
    assert str(args.inputs[0]) == str(await source.resolve(strict=True))


@pytest.mark.anyio
async def test_parser_invoke_raises_for_missing_input(
    tmp_path: PathLike[str],
) -> None:
    """Parser ``invoke`` should fail fast when an input path cannot be resolved."""
    missing = Path(tmp_path) / "does-not-exist.xcf"
    ns = split.parser().parse_args([str(missing)])

    with pytest.raises(ExceptionGroup) as exc_info:
        await ns.invoke(ns)

    assert any(
        isinstance(error, FileNotFoundError) for error in exc_info.value.exceptions
    )


def test_module_main_invokes_run(run_module_helper: RunModuleHelper) -> None:
    """Executing the module as a script should call ``asyncer.runnify``."""
    called = run_module_helper("scripts.split", ["scripts.split"])
    assert called["ran"] is True
