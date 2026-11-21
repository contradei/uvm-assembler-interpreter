"""Stage 2 entry point: JSON assembly to binary machine code."""

from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'src.uvm'

from .cli import parse_args
from .codec import encode_program, format_bytes
from .files import atomic_write
from .parser import read_program


def assemble(args):
    """Write the machine code, report count and optionally print each byte."""
    program = read_program(args.source)
    chunks = encode_program(program)
    atomic_write(args.output, b''.join(chunks))
    print(f'Instructions: {len(chunks)}')
    if args.test_mode:
        for chunk in chunks:
            print(format_bytes(chunk))


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
