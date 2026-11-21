"""Command-line options for the stage 1 assembler."""

import argparse
from pathlib import Path


def different_paths(source, output):
    """Prevent output from overwriting the input, including hard links."""
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve():
        raise ValueError('input and output paths must differ')
    if output.exists() and source.samefile(output):
        raise ValueError('input and output refer to the same file')
    if output.is_dir():
        raise ValueError('output path is a directory')


def parse_args(argv=None):
    """Parse the assembler source, binary destination and test mode."""
    parser = argparse.ArgumentParser(description='UVM variant 9')
    commands = parser.add_subparsers(dest='command', required=True)
    assembler = commands.add_parser('assemble', help='assemble JSON source')
    assembler.add_argument('--source', required=True, type=Path)
    assembler.add_argument('--output', required=True, type=Path)
    assembler.add_argument('--test-mode', action='store_true')
    args = parser.parse_args(argv)
    try:
        if not args.source.is_file():
            raise ValueError('source file does not exist')
        different_paths(args.source, args.output)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    return args
