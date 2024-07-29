from anyio import Path as _Path
from argparse import (
    ArgumentParser as _ArgParser,
    Namespace as _NS,
    ONE_OR_MORE as _ONE_OR_MORE,
)
from asyncio import gather as _gather, run as _run
from dataclasses import dataclass as _dc
from functools import wraps as _wraps
from itertools import cycle as _cycle
from logging import INFO as _INFO, basicConfig as _basicConfig
from sys import argv as _argv
from typing import Callable as _Call, Sequence as _Seq, final as _fin


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
    async def unsplit(path: _Path):
        async def splitPaths():
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
        await main(Arguments(inputs=args.inputs))

    parser.set_defaults(invoke=invoke)
    return parser


if __name__ == "__main__":
    _basicConfig(level=_INFO)
    entry = parser().parse_args(_argv[1:])
    _run(entry.invoke(entry))
