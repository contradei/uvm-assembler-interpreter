"""CLI parameter validation without altering user files."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from src.uvm.cli import parse_args
from src.uvm.main import main


class CliTests(unittest.TestCase):
    """Invalid paths and flags must fail before any output is written."""

    def test_required_arguments(self):
        """Require a subcommand and both assembly file arguments."""
        for args in ([], ['assemble'], ['assemble', '--source', 'missing']):
            with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
                parse_args(args)

    def test_help(self):
        """Top-level help works without specifying files."""
        with redirect_stdout(StringIO()), self.assertRaises(SystemExit) as cm:
            parse_args(['--help'])
        self.assertEqual(cm.exception.code, 0)

    def test_path_errors(self):
        """Prevent overwrite, directory destinations and nonexistent inputs."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'test.json'
            source.write_text('[]', encoding='utf-8')
            for output in (source, Path(directory)):
                args = ['assemble', '--source', str(source),
                        '--output', str(output)]
                with redirect_stderr(StringIO()):
                    with self.assertRaises(SystemExit):
                        parse_args(args)
            source.unlink()
            with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
                parse_args(args)

    def test_bad_source_keeps_output(self):
        """Malformed assembly cannot replace an existing output file."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'test.json'
            output = Path(directory) / 'test.bin'
            source.write_text('[{"op":"bad"}]', encoding='utf-8')
            output.write_bytes(b'previous')
            args = ['assemble', '--source', str(source),
                    '--output', str(output)]
            with redirect_stderr(StringIO()):
                self.assertEqual(main(args), 1)
            self.assertEqual(output.read_bytes(), b'previous')
