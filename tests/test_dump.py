"""Inclusive XML dump boundaries and transactional interpreter output."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree

from src.uvm.dump import memory_xml, validate_range
from src.uvm.machine import Memory
from src.uvm.main import main


class DumpTests(unittest.TestCase):
    """Inspect parsed XML, not only formatted output strings."""

    def test_inclusive_range(self):
        """Include both endpoints and unwritten zero cells."""
        memory = Memory()
        memory.write(10, 99)
        root = ElementTree.fromstring(memory_xml(memory, 9, 11))
        self.assertEqual(root.attrib, {'start': '9', 'end': '11'})
        self.assertEqual([(c.get('address'), c.get('value')) for c in root],
                         [('9', '0'), ('10', '99'), ('11', '0')])

    def test_single_last_cell(self):
        """A single-cell dump at the largest address is valid."""
        last = 2**21 - 1
        root = ElementTree.fromstring(memory_xml(Memory(), last, last))
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].get('address'), str(last))

    def test_bad_ranges(self):
        """Reject reversed, negative and out-of-space ranges."""
        for start, end in ((1, 0), (-1, 0), (0, 2**21)):
            with self.assertRaises(ValueError):
                validate_range(start, end)

    def test_invalid_binary_preserves_dump(self):
        """A failed run must not overwrite an existing successful dump."""
        with tempfile.TemporaryDirectory() as folder:
            binary, dump = Path(folder) / 'in.bin', Path(folder) / 'out.xml'
            binary.write_bytes(b'\x00')
            dump.write_bytes(b'previous')
            args = ['interpret', '--binary', str(binary), '--dump', str(dump),
                    '--start', '0', '--end', '2']
            with redirect_stderr(StringIO()):
                self.assertEqual(main(args), 1)
            self.assertEqual(dump.read_bytes(), b'previous')

    def test_cli_execution(self):
        """Run a known binary through the CLI and parse its actual XML file."""
        with tempfile.TemporaryDirectory() as folder:
            binary, dump = Path(folder) / 'in.bin', Path(folder) / 'out.xml'
            binary.write_bytes(bytes.fromhex('6c3700000002000000'))
            args = ['interpret', '--binary', str(binary), '--dump', str(dump),
                    '--start', '0', '--end', '0']
            with redirect_stdout(StringIO()):
                self.assertEqual(main(args), 0)
            self.assertEqual(ElementTree.parse(dump).getroot()[0].get('value'),
                             '443')
