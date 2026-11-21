"""Decode machine code, preserve instruction memory and copy an array."""

from pathlib import Path
import unittest

from src.uvm.codec import decode_instruction, encode_instruction, encode_program
from src.uvm.machine import Machine, Memory
from src.uvm.parser import read_program


class DecoderTests(unittest.TestCase):
    """Test decoding against independent bytes and malformed input."""

    def test_golden_decoding(self):
        """Recover both NOT addresses and the following byte offset."""
        fields, following = decode_instruction(bytes.fromhex('995a000c0a00'), 0)
        self.assertEqual(fields, {'a': 25, 'b': 724, 'c': 643})
        self.assertEqual(following, 6)

    def test_truncated(self):
        """Every shortened prefix of each valid instruction is rejected."""
        for text in ('6c37000000', '015a0000', 'c2450000', '995a000c0a00'):
            data = bytes.fromhex(text)
            for length in range(len(data)):
                with self.assertRaises(ValueError):
                    decode_instruction(data[:length], 0)

    def test_invalid_code(self):
        """Unknown opcodes and nonzero unused bits are not silently ignored."""
        for text in ('00', '1f', '0c000000e0', '01000004', '190000000080'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                decode_instruction(bytes.fromhex(text), 0)


class MachineTests(unittest.TestCase):
    """Memory operations do not alias code bytes or silently wrap addresses."""

    def test_array_copy(self):
        """Copy the three initialized words from 10..12 to 20..22."""
        root = Path(__file__).resolve().parents[1]
        source = read_program(root / 'examples' / 'copy_array.json')
        code = b''.join(encode_program(source))
        machine = Machine(code)
        memory = machine.run()
        self.assertEqual([memory.read(i) for i in range(10, 13)],
                         [7, 0, 4294967295])
        self.assertEqual([memory.read(i) for i in range(20, 23)],
                         [7, 0, 4294967295])
        self.assertEqual(machine.executed, 12)
        self.assertEqual(machine.code, code)
        self.assertEqual(machine.position, len(code))

    def test_initial_state(self):
        """Start with zeros and accept an empty program."""
        machine = Machine(b'')
        self.assertEqual(machine.accumulator, 0)
        self.assertEqual(machine.run().read(2**21 - 1), 0)
        self.assertEqual(machine.executed, 0)

    def test_memory_bounds(self):
        """Enforce address and word widths independently of parsing."""
        memory = Memory()
        for address in (-1, 2**21, True):
            with self.assertRaises(ValueError):
                memory.read(address)
        for value in (-1, 2**32, True):
            with self.assertRaises(ValueError):
                memory.write(0, value)

    def test_code_memory_separation(self):
        """Writing data address zero cannot corrupt the first instruction."""
        code = (bytes.fromhex('6c37000000')
                + encode_instruction({'a': 2, 'b': 0}))
        machine = Machine(code)
        self.assertEqual(machine.run().read(0), 443)
        self.assertEqual(machine.code, code)

    def test_not_unavailable(self):
        """Stage 3 explicitly rejects the still-unimplemented ALU operation."""
        machine = Machine(bytes.fromhex('995a000c0a00'))
        with self.assertRaisesRegex(ValueError, 'stage 4'):
            machine.run()
