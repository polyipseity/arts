#!/usr/bin/env python
"""Split large files into fixed-size chunks and provide a CLI parser.

This module exposes a small CLI-friendly API used by the package tests:
- `Arguments`: dataclass holding input path(s)
- `main`: coroutine that splits files concurrently into numbered parts
- `parser`: returns an `argparse.ArgumentParser` with an async `invoke` adapter
"""

from argparse import ONE_OR_MORE, ArgumentParser, Namespace
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import wraps
from itertools import cycle
from logging import INFO, basicConfig
from sys import argv
from typing import final

from anyio import Path, open_file
from asyncer import SoonValue, create_task_group, runnify
from asyncstdlib import enumerate as aenumerate

"""Public symbols exported by this module."""
__all__ = ("Arguments", "main", "parser")

"""Default chunk size in bytes (10 MiB) when splitting large files."""
_SPLIT_SIZE = 10 * 1024**2  # 10 MiB


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
    """Immutable container for the script's command-line inputs.

    Attributes:
        inputs: Sequence of `anyio.Path` objects to process.
    """

    inputs: Sequence[Path]

    def __post_init__(self):
        """Normalize `inputs` into an immutable tuple after construction."""
        object.__setattr__(self, "inputs", tuple(self.inputs))


async def main(args: Arguments):
    """Split each input file into fixed-size chunk files concurrently.

    The function spawns a per-path task that writes numbered chunk files
    using the `_SPLIT_SIZE` constant.
    """

    async def split(path: Path):
        """Split a single file into sequentially numbered binary chunks.

        Output files are named `"{orig}.{NNN}"` where `NNN` is a three-digit
        sequence number starting at 001. Any previously-existing trailing
        chunk files beyond the last used index are removed.
        """
        async with await path.open(mode="rb") as file:

            async def chunks():
                """Asynchronously yield successive binary chunks from the open file."""
                chunk = await file.read(_SPLIT_SIZE)
                while chunk:
                    yield chunk
                    chunk = await file.read(_SPLIT_SIZE)

            count = 0
            async for count, chunk in aenumerate(chunks(), 1):
                async with await open_file(
                    "{}.{:03}".format(path, count), mode="wb"
                ) as split:
                    await split.write(chunk)

            for count, _ in enumerate(cycle((None,)), count + 1):
                try:
                    old_file = await Path("{}.{:03}".format(path, count)).resolve(
                        strict=True
                    )
                except FileNotFoundError:
                    break
                await old_file.unlink(missing_ok=False)

    async with create_task_group() as tg:
        for inp in args.inputs:
            tg.soonify(split)(inp)


def parser(parent: Callable[..., ArgumentParser] | None = None):
    """Create and return an `ArgumentParser` configured for this module.

    The parser registers an async `invoke` function on the parsed namespace
    that resolves input paths and calls `main` with a populated `Arguments`.
    """
    prog = __package__ or __name__

    parser = (ArgumentParser if parent is None else parent)(
        prog=f"python -m {prog}",
        description="split file(s)",
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
        """ArgumentParser `invoke` adapter: resolve inputs and call `main`."""
        resolved: list[SoonValue[Path]] = []
        async with create_task_group() as tg:
            for inp in args.inputs:
                soon = tg.soonify(Path.resolve)(inp, strict=True)
                resolved.append(soon)

        await main(Arguments(inputs=[r.value for r in resolved]))

    parser.set_defaults(invoke=invoke)
    return parser


async def main0():
    """Entry point for running the script directly. Parses CLI arguments and invokes main()."""
    basicConfig(level=INFO)
    entry = parser().parse_args(argv[1:])
    await entry.invoke(entry)


def __main__():
    """Entry point for running the script directly."""
    runnify(main0, backend_options={"use_uvloop": True})()


if __name__ == "__main__":
    __main__()
