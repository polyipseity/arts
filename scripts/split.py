"""Split large files into fixed-size chunks and provide a CLI parser.

This module exposes a small CLI-friendly API used by the package tests:
- `Arguments`: dataclass holding input path(s)
- `main`: coroutine that splits files concurrently into numbered parts
- `parser`: returns an `argparse.ArgumentParser` with an async `invoke` adapter
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
from functools import partial as _partial
from functools import wraps as _wraps
from itertools import cycle as _cycle
from logging import INFO as _INFO
from logging import basicConfig as _basicConfig
from sys import argv as _argv
from typing import final as _fin

from anyio import Path as _Path
from anyio import open_file as _open_f
from asyncstdlib import enumerate as _aenumerate

__all__ = ("Arguments", "main", "parser")

_SPLIT_SIZE = 10 * 1024**2  # 10 MiB


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
    """Immutable container for the script's command-line inputs.

    Attributes:
        inputs: Sequence of `anyio.Path` objects to process.
    """

    inputs: _Seq[_Path]

    def __post_init__(self):
        """Normalize `inputs` into an immutable tuple after construction."""
        object.__setattr__(self, "inputs", tuple(self.inputs))


async def main(args: Arguments):
    """Split each input file into fixed-size chunk files concurrently.

    The function spawns a per-path task that writes numbered chunk files
    using the `_SPLIT_SIZE` constant.
    """

    async def split(path: _Path):
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
            async for count, chunk in _aenumerate(chunks(), 1):
                async with await _open_f(
                    "{}.{:03}".format(path, count), mode="wb"
                ) as split:
                    await split.write(chunk)

            for count, _ in enumerate(_cycle((None,)), count + 1):
                try:
                    old_file = await _Path("{}.{:03}".format(path, count)).resolve(
                        strict=True
                    )
                except FileNotFoundError:
                    break
                await old_file.unlink(missing_ok=False)

    await _gather(*map(split, args.inputs))


def parser(parent: _Call[..., _ArgParser] | None = None):
    """Create and return an `ArgumentParser` configured for this module.

    The parser registers an async `invoke` function on the parsed namespace
    that resolves input paths and calls `main` with a populated `Arguments`.
    """
    prog = __package__ or __name__

    parser = (_ArgParser if parent is None else parent)(
        prog=f"python -m {prog}",
        description="split file(s)",
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
        """ArgumentParser `invoke` adapter: resolve inputs and call `main`."""
        await main(
            Arguments(
                inputs=await _gather(
                    *map(
                        _partial(_Path.resolve, strict=True),
                        args.inputs,
                    )
                ),
            )
        )

    parser.set_defaults(invoke=invoke)
    return parser


if __name__ == "__main__":
    _basicConfig(level=_INFO)
    entry = parser().parse_args(_argv[1:])
    _run(entry.invoke(entry))
