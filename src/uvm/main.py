"""Stage 3: assemble JSON or interpret the basic memory instructions."""

from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = 'src.uvm'

from .cli import parse_args
from .codec import encode_program, format_bytes
from .files import atomic_write
from .dump import memory_xml
from .machine import Machine
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
        if args.command == 'assemble':
            assemble(args)
        else:
            interpret(args)
    except (ValueError, OSError, RecursionError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1
    return 0


def interpret(args):
    """Run a binary program and publish an XML dump only after success."""
    machine = Machine(args.binary.read_bytes())
    memory = machine.run()
    atomic_write(args.dump, memory_xml(memory, args.start, args.end))
    print(f'Executed: {machine.executed}')
    print(f'Dump: {args.dump}')


if __name__ == '__main__':
    raise SystemExit(main())
