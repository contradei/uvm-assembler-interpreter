"""Stage-specific output and side-effect checks."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from src.uvm.main import main


class StageTests(unittest.TestCase):
    """Stage 2 writes exact bytes and prints the instruction count."""

    def test_assemble(self):
        """Test mode prints bytes; normal mode only reports the count."""
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / 'in.json', Path(folder) / 'out.bin'
            source.write_text('[{"op":"load_const","value":443}]',
                              encoding='utf-8')
            args = ['assemble', '--source', str(source),
                    '--output', str(output)]
            text = StringIO()
            with redirect_stdout(text):
                self.assertEqual(main(args + ['--test-mode']), 0)
            self.assertEqual(text.getvalue(),
                             'Instructions: 1\n'
                             '0x6C, 0x37, 0x00, 0x00, 0x00\n')
            self.assertEqual(output.read_bytes(), bytes.fromhex('6c37000000'))
            text = StringIO()
            with redirect_stdout(text):
                self.assertEqual(main(args), 0)
            self.assertEqual(text.getvalue(), 'Instructions: 1\n')
