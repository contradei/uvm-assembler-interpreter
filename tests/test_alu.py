"""Bitwise NOT semantics, aliasing and accumulator preservation."""

from pathlib import Path
import unittest

from src.uvm.codec import encode_program
from src.uvm.machine import Machine
from src.uvm.parser import read_program


class AluTests(unittest.TestCase):
    """NOT reads C, writes B and leaves unrelated state unchanged."""

    def test_cases_program(self):
        """Execute independent boundary examples through assembled code."""
        root = Path(__file__).resolve().parents[1]
        source = read_program(root / 'examples' / 'not_cases.json')
        machine = Machine(b''.join(encode_program(source)))
        memory = machine.run()
        self.assertEqual([memory.read(i) for i in range(10, 14)],
                         [4294967295, 0, 2147483647, 1431655765])
        self.assertEqual([memory.read(i) for i in range(4)],
                         [0, 4294967295, 2147483648, 2863311530])

    def test_accumulator_and_neighbors(self):
        """A destination distinct from the source changes only that cell."""
        machine = Machine(bytes.fromhex('995a000c0a00'))
        machine.accumulator = 123
        machine.memory.write(643, 15)
        machine.memory.write(723, 77)
        machine.memory.write(725, 88)
        memory = machine.run()
        self.assertEqual(memory.read(724), 4294967280)
        self.assertEqual(memory.read(643), 15)
        self.assertEqual((memory.read(723), memory.read(725)), (77, 88))
        self.assertEqual(machine.accumulator, 123)

    def test_in_place_and_double_not(self):
        """Complementing the same cell twice restores its original value."""
        fields = {'a': 25, 'b': 3, 'c': 3}
        code = b''.join(encode_program([fields, fields]))
        machine = Machine(code)
        machine.memory.write(3, 305419896)
        self.assertEqual(machine.run().read(3), 305419896)

    def test_last_address(self):
        """The largest 21-bit address can be both source and destination."""
        last = 2**21 - 1
        code = b''.join(encode_program([{'a': 25, 'b': last, 'c': last}]))
        machine = Machine(code)
        self.assertEqual(machine.run().read(last), 4294967295)
