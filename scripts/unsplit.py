#!/usr/bin/env python
"""Reassemble files that were previously split by `split.py`.

Provides a small CLI-friendly API:
- `Arguments`: dataclass for CLI inputs
- `main`: coroutine that concatenates numbered chunk files
- `parser`: returns an argparse.ArgumentParser with an `invoke` adapter
"""

from argparse import ONE_OR_MORE, ArgumentParser, Namespace
from asyncio import gather, run
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import wraps
from itertools import cycle
from logging import INFO, basicConfig
from sys import argv
from typing import final

from anyio import Path

"""Public symbols exported by this module."""
__all__ = ("Arguments", "main", "parser")


@final
@dataclass(
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

    inputs: Sequence[Path]

    def __post_init__(self):
        """Normalize `inputs` into an immutable tuple after construction."""
        object.__setattr__(self, "inputs", tuple(self.inputs))


async def main(args: Arguments):
    """Concatenate numbered chunk files for each provided target path.

    For each `path` this coroutine will open `{path}.001`, `{path}.002`, ... in
    order and write their contents to `path` until no further chunk files are
    found.
    """

    async def unsplit(path: Path):
        """Assemble a single target file by iterating its chunk files."""

        async def splitPaths():
            """Yield resolved `Path` objects for each numbered chunk for `path`."""
            for count, _ in enumerate(cycle((None,)), 1):
                try:
                    yield await Path("{}.{:03}".format(path, count)).resolve(
                        strict=True
                    )
                except FileNotFoundError:
                    break

        async with await path.open(mode="wb") as file:
            async for splitPath in splitPaths():
                async with await splitPath.open(mode="rb") as split:
                    await file.write(await split.read())

    await gather(*map(unsplit, args.inputs))


def parser(parent: Callable[..., ArgumentParser] | None = None):
    """Return an `ArgumentParser` configured for `unsplit` CLI usage.

    The parser registers an async `invoke` that forwards parsed inputs to
    `main`.
    """
    prog = __package__ or __name__

    parser = (ArgumentParser if parent is None else parent)(
        prog=f"python -m {prog}",
        description="unsplit file(s)",
        add_help=True,
        allow_abbrev=False,
        exit_on_error=False,
    )
    parser.add_argument(
        "inputs",
        action="store",
        nargs=ONE_OR_MORE,
        type=Path,
        help="sequence of input(s) to read",
    )

    @wraps(main)
    async def invoke(args: Namespace):
        """ArgumentParser `invoke` adapter — call `main` with Arguments."""
        await main(Arguments(inputs=args.inputs))

    parser.set_defaults(invoke=invoke)
    return parser


if __name__ == "__main__":
    basicConfig(level=INFO)
    """Parsed CLI namespace used to invoke the async entrypoint."""
    entry = parser().parse_args(argv[1:])
    run(entry.invoke(entry))
