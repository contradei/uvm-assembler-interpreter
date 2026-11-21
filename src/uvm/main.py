"""Stage 1 entry point: JSON to intermediate instruction fields."""

from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'src.uvm'

from .cli import parse_args
from .parser import format_fields, read_program


def assemble(args):
    """Parse all instructions; show fields only when test mode is enabled."""
    program = read_program(args.source)
    if args.test_mode:
        for fields in program:
            print(format_fields(fields))


def main(argv=None):
    """Return code 1 for processing errors and leave argparse code 2 intact."""
    args = parse_args(argv)
    try:
        assemble(args)
    except (ValueError, OSError, RecursionError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
