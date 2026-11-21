"""Stage-specific output and side-effect checks."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from src.uvm.main import main


class StageTests(unittest.TestCase):
    """Stage 1 prints fields but does not create machine code yet."""

    def test_assemble(self):
        """The output path is accepted without writing a fake binary file."""
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / 'in.json', Path(folder) / 'out.bin'
            source.write_text('[{"op":"load_const","value":443}]',
                              encoding='utf-8')
            args = ['assemble', '--source', str(source),
                    '--output', str(output)]
            text = StringIO()
            with redirect_stdout(text):
                self.assertEqual(main(args + ['--test-mode']), 0)
            self.assertEqual(text.getvalue(), 'A=12, B=443\n')
            self.assertFalse(output.exists())
            text = StringIO()
            with redirect_stdout(text):
                self.assertEqual(main(args), 0)
            self.assertEqual(text.getvalue(), '')
