"""Behavior tests for :mod:`scripts.unsplit`.

These tests mirror the source layout and emphasize happy/failure-path
coverage for file reassembly semantics.
"""

from os import PathLike

import pytest
from anyio import Path

from scripts import unsplit

from ..utils import RunModuleHelper

"""Public symbols exported by this module (none)."""
__all__ = ()


def test_arguments_normalize_inputs_to_tuple_and_are_frozen() -> None:
    """``Arguments`` should normalize inputs to tuple and remain immutable."""
    args = unsplit.Arguments(inputs=[Path("a"), Path("b")])
    assert isinstance(args.inputs, tuple)
    assert args.inputs == (Path("a"), Path("b"))
    assert unsplit.Arguments.__dataclass_params__.frozen is True


@pytest.mark.anyio
async def test_main_reassembles_file_from_chunks(tmp_path: PathLike[str]) -> None:
    """Unsplit should concatenate numbered chunks into the target file."""
    target = Path(tmp_path) / "image.xcf"
    await Path(f"{target}.001").write_bytes(b"ABC")
    await Path(f"{target}.002").write_bytes(b"DEF")

    await unsplit.main(unsplit.Arguments(inputs=[target]))

    assert await target.read_bytes() == b"ABCDEF"


@pytest.mark.anyio
async def test_main_stops_when_chunk_sequence_has_a_gap(tmp_path: PathLike[str]) -> None:
    """A missing middle chunk should stop concatenation at the first gap."""
    target = Path(tmp_path) / "gap.xcf"
    await Path(f"{target}.001").write_bytes(b"ONE")
    await Path(f"{target}.003").write_bytes(b"THREE")

    await unsplit.main(unsplit.Arguments(inputs=[target]))

    assert await target.read_bytes() == b"ONE"


@pytest.mark.anyio
async def test_main_overwrites_existing_target_when_no_chunks_found(
    tmp_path: PathLike[str],
) -> None:
    """No chunk files should leave the target present but empty."""
    target = Path(tmp_path) / "missing.xcf"
    await target.write_bytes(b"previous-data")

    await unsplit.main(unsplit.Arguments(inputs=[target]))

    assert await target.read_bytes() == b""


@pytest.mark.anyio
async def test_main_processes_multiple_targets(tmp_path: PathLike[str]) -> None:
    """Multiple target files should be unsplit independently in one call."""
    first = Path(tmp_path) / "first.xcf"
    second = Path(tmp_path) / "second.xcf"

    await Path(f"{first}.001").write_bytes(b"A")
    await Path(f"{first}.002").write_bytes(b"B")
    await Path(f"{second}.001").write_bytes(b"X")
    await Path(f"{second}.002").write_bytes(b"Y")

    await unsplit.main(unsplit.Arguments(inputs=[first, second]))

    assert await first.read_bytes() == b"AB"
    assert await second.read_bytes() == b"XY"


def test_parser_parses_inputs_as_anyio_paths() -> None:
    """CLI parser should convert positional inputs into ``anyio.Path`` objects."""
    ns = unsplit.parser().parse_args(["a.xcf", "b.xcf"])
    assert len(ns.inputs) == 2
    assert all(isinstance(path, Path) for path in ns.inputs)


@pytest.mark.anyio
async def test_parser_invoke_calls_main_with_arguments(
    tmp_path: PathLike[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Parser ``invoke`` should pass parsed inputs to ``main`` as ``Arguments``."""
    target = Path(tmp_path) / "target.xcf"
    captured: dict[str, unsplit.Arguments] = {}

    async def fake_main(args: unsplit.Arguments) -> None:
        """Capture main arguments for parser invocation assertions."""
        captured["args"] = args

    monkeypatch.setattr(unsplit, "main", fake_main)

    ns = unsplit.parser().parse_args([str(target)])
    await ns.invoke(ns)

    args = captured["args"]
    assert isinstance(args, unsplit.Arguments)
    assert args.inputs == (target,)


def test_module_main_invokes_run(run_module_helper: RunModuleHelper) -> None:
    """Executing the module as a script should call ``asyncer.runnify``."""
    called = run_module_helper("scripts.unsplit", ["scripts.unsplit"])
    assert called["ran"] is True
