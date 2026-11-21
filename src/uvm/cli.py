"""Command-line options for assembly and interpretation."""

import argparse
from pathlib import Path

from .dump import validate_range


def different_paths(source, output):
    """Prevent output from overwriting the input, including hard links."""
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve():
        raise ValueError('input and output paths must differ')
    if output.exists() and source.samefile(output):
        raise ValueError('input and output refer to the same file')
    if output.is_dir():
        raise ValueError('output path is a directory')


def add_assembler(commands):
    """Describe the source, binary output and diagnostic flag."""
    assembler = commands.add_parser('assemble', help='assemble JSON source')
    assembler.add_argument('--source', required=True, type=Path)
    assembler.add_argument('--output', required=True, type=Path)
    assembler.add_argument('--test-mode', action='store_true')


def add_interpreter(commands):
    """Describe the binary input and inclusive XML dump range."""
    interpreter = commands.add_parser('interpret', help='execute machine code')
    interpreter.add_argument('--binary', required=True, type=Path)
    interpreter.add_argument('--dump', required=True, type=Path)
    interpreter.add_argument('--start', required=True, type=int)
    interpreter.add_argument('--end', required=True, type=int)


def validate_paths(args):
    """Validate subcommand-specific paths and dump endpoints."""
    if args.command == 'assemble':
        source, output = args.source, args.output
    else:
        source, output = args.binary, args.dump
        validate_range(args.start, args.end)
    if not source.is_file():
        raise ValueError('input file does not exist')
    different_paths(source, output)


def parse_args(argv=None):
    """Return validated options, reporting argument errors with code 2."""
    parser = argparse.ArgumentParser(description='UVM variant 9')
    commands = parser.add_subparsers(dest='command', required=True)
    add_assembler(commands)
    add_interpreter(commands)
    args = parser.parse_args(argv)
    try:
        validate_paths(args)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    return args
