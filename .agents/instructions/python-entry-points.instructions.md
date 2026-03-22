---
name: Python entry points
description: Convention for writing Python scripts and modules with __name__ == "__main__" entry points
applyTo: "**/*.py"
---

# Python Entry Points Convention (self/arts)

This document establishes the convention for Python scripts and modules in the arts project that expose entry points for direct execution. All scripts in `scripts/` must follow this pattern.

**Inheritance note:** This convention extends the parent repository's Python entry points convention (see `../../.agents/instructions/python-entry-points.instructions.md`). Local scripts follow the same `__main__ == "__main__"` pattern with Asyncer integration. Refer to the parent documentation for comprehensive guidance; this file provides arts-specific context.

## Quick Pattern (Async)

```python
"""Script purpose and usage."""

from asyncer import runnify


async def main(argv: list[str] | None = None) -> None:
    """Main async entry point."""
    if argv is None:
        import sys
        argv = sys.argv[1:]

    # application logic here
    pass


def __main__() -> None:
    """Entry point for running the script directly."""
    runnify(main, backend_options={"use_uvloop": True})()


if __name__ == "__main__":
    __main__()
```

## Quick Pattern (Sync)

```python
"""Script purpose and usage."""


def main(argv: list[str] | None = None) -> None:
    """Main sync entry point."""
    if argv is None:
        import sys
        argv = sys.argv[1:]

    # application logic here
    pass


def __main__() -> None:
    """Entry point for running the script directly."""
    main()


if __name__ == "__main__":
    __main__()
```

## Arts-Specific Rules

1. **Script location & invocation**: All utility scripts live in `scripts/` and are run via the Python environment. Always use the local `.venv` environment when available.

2. **Argument handling**: Scripts in arts typically process `.xcf.*` files or metadata. Accept arguments via `argv` parameter in `main()`. Parse arguments inside `main()` to keep it testable.

3. **Error handling**: Use exit codes consistently:
   - `0`: Success
   - `1`: General error
   - `2`: Argument parsing error
   - `3`: File/IO error (file not found, permission denied, etc.)
   - Example:

     ```python
     try:
         xcf_path = Path(argv[0]) if argv else DEFAULT_XCF
         if not xcf_path.exists():
             print(f"File not found: {xcf_path}", file=sys.stderr)
             return exit(3)
     except Exception as e:
         print(f"Error: {e}", file=sys.stderr)
         return exit(1)
     ```

4. **Type hints & enforcement**: Arts project enforces strict type checking with `pyright` in strict mode. Always include complete type hints:
   - Function parameters and return types
   - Use `collections.abc.Sequence[str]` for sequences
   - Use `os.PathLike` for file paths
   - Example: `async def main(argv: Sequence[str] | None = None) -> None:`

5. **Docstrings (mandatory)**: The arts project enforces module-level and function docstrings through `tests/test_docstrings.py`. Every module and exported function must have a docstring:

   ```python
   """Process and split .xcf files into chunks.

   Usage:
       python -m scripts.split --input artwork.xcf --chunk-size 10

   Splits large .xcf files into numbered chunks for better versioning.
   """
   ```

6. **Public API declaration**: Include `__all__` as a `tuple[str, ...]` at module level:

   ```python
   __all__ = ("main",)
   ```

7. **Testing**: Import `main` directly in tests; do not trigger the entry point guard. Use `@pytest.mark.anyio` for async tests:

   ```python
   @pytest.mark.anyio
   async def test_main_splits_xcf(tmp_path):
       from scripts.split import main
       await main(['--input', str(tmp_path / 'test.xcf')])
   ```

## Integration with Parent Convention

This arts project inherits the parent repository's Python entry points convention. Refer to `../../.agents/instructions/python-entry-points.instructions.md` for:

- Detailed rationale and background
- Integration with argparse and Click
- Comprehensive testing patterns
- Error handling best practices
- Asyncer helper functions (`asyncify`, `soonify`, `create_task_group`)

## Implementation Checklist for Arts Scripts

When writing a new script or updating an existing one:

- [ ] Define `main()` as the primary logic (async or sync)
- [ ] Accept optional `argv: Sequence[str] | None = None` parameter in `main()`
- [ ] Define `__main__()` sync wrapper calling `main()` (with `runnify` for async)
- [ ] Place `if __name__ == "__main__":` guard at file end, calling `__main__()`
- [ ] Include return type hints: `-> None` for both functions
- [ ] Add module-level docstring with usage example (required by test suite)
- [ ] Add docstrings to `main()` and `__main__()` (required by test suite)
- [ ] Declare `__all__` as `tuple[str, ...]` at module level
- [ ] Use appropriate exit codes (0, 1, 2, 3)
- [ ] Include complete type hints on all functions and parameters
- [ ] Test by importing `main()` directly; do not trigger the guard
- [ ] Run `pyright`, `ruff check`, and `pytest` locally before committing
- [ ] Verify `tests/test_docstrings.py` and `tests/test_module_exports.py` pass

## Examples

### Example 1: Split XCF File (Sync)

```python
"""Split a .xcf file into numbered chunks for better version control.

Usage:
    python -m scripts.split --input big-artwork.xcf --chunk-size 50

Chunks are written to the same directory as the input file with
numeric suffixes (e.g., big-artwork.xcf.00, big-artwork.xcf.01).
"""

import sys
from pathlib import Path
from typing import Sequence
import argparse

__all__ = ("main",)


def split_xcf_file(path: Path, chunk_size: int) -> int:
    """Split a .xcf file into chunks. Returns number of chunks created."""
    # implementation
    return 0


def main(argv: Sequence[str] | None = None) -> None:
    """Main entry point for splitting .xcf files."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Split .xcf files into chunks")
    parser.add_argument("--input", required=True, help="Input .xcf file path")
    parser.add_argument("--chunk-size", type=int, default=50, help="Chunk size in MB")
    args = parser.parse_args(argv)

    xcf_path = Path(args.input)
    if not xcf_path.exists():
        print(f"File not found: {xcf_path}", file=sys.stderr)
        return exit(3)

    try:
        num_chunks = split_xcf_file(xcf_path, args.chunk_size)
        print(f"✓ Split into {num_chunks} chunks")
        return exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return exit(1)


def __main__() -> None:
    """Entry point for running the script directly."""
    main()


if __name__ == "__main__":
    __main__()
```

### Example 2: Async Metadata Processing

```python
"""Process and validate artwork metadata across multiple files.

Usage:
    python -m scripts.validate-metadata --directory ./arts

Checks metadata consistency, validates file references, and reports issues.
"""

import sys
from pathlib import Path
from typing import Sequence
from asyncer import runnify, asyncify
import argparse

__all__ = ("main",)


async def validate_directory(dirpath: Path) -> tuple[int, int]:
    """Validate all artwork files in a directory asynchronously.

    Returns (total_files, errors_found).
    """
    # Use asyncify for blocking operations
    files = await asyncify(list)(dirpath.glob("**/*.xcf*"))
    errors = 0
    for fpath in files:
        # validation logic
        pass
    return len(files), errors


async def main(argv: Sequence[str] | None = None) -> None:
    """Main async entry point for metadata validation."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Validate artwork metadata")
    parser.add_argument("--directory", required=True, help="Directory to scan")
    args = parser.parse_args(argv)

    dirpath = Path(args.directory)
    if not dirpath.is_dir():
        print(f"Not a directory: {dirpath}", file=sys.stderr)
        return exit(3)

    try:
        total, errors = await validate_directory(dirpath)
        print(f"✓ Validated {total} files, {errors} errors found")
        return exit(0 if errors == 0 else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return exit(1)


def __main__() -> None:
    """Entry point for running the script directly."""
    runnify(main, backend_options={"use_uvloop": True})()


if __name__ == "__main__":
    __main__()
```

## See Also

- Parent repository convention: `../../.agents/instructions/python-entry-points.instructions.md`
- Testing guidance: `testing.instructions.md`
- Module exports & docstrings: `tests/test_module_exports.py`, `tests/test_docstrings.py`
- Type checking: `pyproject.toml` (pyright strict mode config)
