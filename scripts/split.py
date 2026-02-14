from anyio import Path as _Path, open_file as _open_f
from argparse import (
    ArgumentParser as _ArgParser,
    Namespace as _NS,
    ONE_OR_MORE as _ONE_OR_MORE,
)
from asyncio import gather as _gather, run as _run
from asyncstdlib import enumerate as _aenumerate
from dataclasses import dataclass as _dc
from functools import partial as _partial, wraps as _wraps
from itertools import cycle as _cycle
from logging import INFO as _INFO, basicConfig as _basicConfig
from sys import argv as _argv
from collections.abc import Callable as _Call, Sequence as _Seq
from typing import final as _fin

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
    inputs: _Seq[_Path]

    def __post_init__(self):
        object.__setattr__(self, "inputs", tuple(self.inputs))


async def main(args: Arguments):
    async def split(path: _Path):
        async with await path.open(mode="rb") as file:

            async def chunks():
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
