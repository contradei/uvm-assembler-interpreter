"""Compile and execute three vectors, checking actual XML output."""

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree

from src.uvm.codec import encode_program
from src.uvm.machine import Machine
from src.uvm.main import main
from src.uvm.parser import read_program


root = Path(__file__).resolve().parents[1]
cases = json.loads((root / 'examples' / 'vectors_expected.json').read_text())


class VectorTests(unittest.TestCase):
    """The task overwrites exactly five original cells, not another array."""

    def test_three_xml_results(self):
        """Run both CLI subcommands and compare all addresses and values."""
        for case in cases:
            with self.subTest(case=case['name']):
                with tempfile.TemporaryDirectory() as folder:
                    self.check_pipeline(case, Path(folder))

    def check_pipeline(self, case, folder):
        """Assemble and interpret one standalone JSON program."""
        source = root / 'examples' / (case['name'] + '.json')
        binary, dump = folder / 'program.bin', folder / 'memory.xml'
        with redirect_stdout(StringIO()):
            status = main(['assemble', '--source', str(source),
                           '--output', str(binary)])
            self.assertEqual(status, 0)
            status = main(['interpret', '--binary', str(binary),
                           '--dump', str(dump), '--start', '100',
                           '--end', '104'])
            self.assertEqual(status, 0)
        self.assertEqual(binary.stat().st_size, 75)
        cells = ElementTree.parse(dump).getroot()
        self.assertEqual([int(c.get('address')) for c in cells],
                         [100, 101, 102, 103, 104])
        self.assertEqual([int(c.get('value')) for c in cells], case['expected'])

    def test_in_place_and_neighbors(self):
        """Confirm source equals destination and neighboring cells survive."""
        for case in cases:
            source = root / 'examples' / (case['name'] + '.json')
            program = read_program(source)
            not_opcode = 25
            operations = [item for item in program if item['a'] == not_opcode]
            self.assertEqual(len(program), 15)
            self.assertEqual(len(operations), 5)
            self.assertTrue(all(item['b'] == item['c'] for item in operations))
            machine = Machine(b''.join(encode_program(program)))
            machine.memory.write(99, 123)
            machine.memory.write(105, 456)
            memory = machine.run()
            self.assertEqual((memory.read(99), memory.read(105)), (123, 456))
            self.assertEqual(machine.executed, 15)
