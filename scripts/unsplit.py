"""Reassemble files that were previously split by `split.py`.

Provides a small CLI-friendly API:
- `Arguments`: dataclass for CLI inputs
- `main`: coroutine that concatenates numbered chunk files
- `parser`: returns an argparse.ArgumentParser with an `invoke` adapter
"""

from argparse import (
    ONE_OR_MORE as _ONE_OR_MORE,
)
from argparse import (
    ArgumentParser as _ArgParser,
)
from argparse import (
    Namespace as _NS,
)
from asyncio import gather as _gather
from asyncio import run as _run
from collections.abc import Callable as _Call
from collections.abc import Sequence as _Seq
from dataclasses import dataclass as _dc
from functools import wraps as _wraps
from itertools import cycle as _cycle
from logging import INFO as _INFO
from logging import basicConfig as _basicConfig
from sys import argv as _argv
from typing import final as _fin

from anyio import Path as _Path

__all__ = ("Arguments", "main", "parser")


@_fin
@_dc(
    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=True,
    match_args=True,
    kw_only=True,
    slots=True,
)
class Arguments:
    """Immutable container for CLI input paths used by `unsplit`.

    Attributes:
        inputs: Sequence of `anyio.Path` objects to be concatenated.
    """

    inputs: _Seq[_Path]

    def __post_init__(self):
        """Normalize `inputs` into an immutable tuple after construction."""
        object.__setattr__(self, "inputs", tuple(self.inputs))


async def main(args: Arguments):
    """Concatenate numbered chunk files for each provided target path.

    For each `path` this coroutine will open `{path}.001`, `{path}.002`, ... in
    order and write their contents to `path` until no further chunk files are
    found.
    """

    async def unsplit(path: _Path):
        """Assemble a single target file by iterating its chunk files."""

        async def splitPaths():
            """Yield resolved `Path` objects for each numbered chunk for `path`."""
            for count, _ in enumerate(_cycle((None,)), 1):
                try:
                    yield await _Path("{}.{:03}".format(path, count)).resolve(
                        strict=True
                    )
                except FileNotFoundError:
                    break

        async with await path.open(mode="wb") as file:
            async for splitPath in splitPaths():
                async with await splitPath.open(mode="rb") as split:
                    await file.write(await split.read())

    await _gather(*map(unsplit, args.inputs))


def parser(parent: _Call[..., _ArgParser] | None = None):
    """Return an `ArgumentParser` configured for `unsplit` CLI usage.

    The parser registers an async `invoke` that forwards parsed inputs to
    `main`.
    """
    prog = __package__ or __name__

    parser = (_ArgParser if parent is None else parent)(
        prog=f"python -m {prog}",
        description="unsplit file(s)",
        add_help=True,
        allow_abbrev=False,
        exit_on_error=False,
    )
    parser.add_argument(
        "inputs",
        action="store",
        nargs=_ONE_OR_MORE,
        type=_Path,
        help="sequence of input(s) to read",
    )

    @_wraps(main)
    async def invoke(args: _NS):
        """ArgumentParser `invoke` adapter — call `main` with Arguments."""
        await main(Arguments(inputs=args.inputs))

    parser.set_defaults(invoke=invoke)
    return parser


if __name__ == "__main__":
    _basicConfig(level=_INFO)
    entry = parser().parse_args(_argv[1:])
    _run(entry.invoke(entry))
