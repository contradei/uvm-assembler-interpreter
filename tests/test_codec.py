"""Independent golden byte sequences and field-width boundary tests."""

from pathlib import Path
import unittest

from src.uvm.codec import encode_instruction, encode_program, format_bytes
from src.uvm.parser import read_program


class CodecTests(unittest.TestCase):
    """Expected bytes are copied from the specification, not re-encoded."""

    def test_golden_sequences(self):
        """Match all four examples byte for byte and their total length."""
        root = Path(__file__).resolve().parents[1]
        program = read_program(root / 'examples' / 'specification.json')
        expected = [bytes.fromhex(text) for text in
                    ('6c37000000', '015a0000', 'c2450000', '995a000c0a00')]
        self.assertEqual(encode_program(program), expected)
        self.assertEqual(len(b''.join(expected)), 19)
        self.assertEqual(format_bytes(expected[1]), '0x01, 0x5A, 0x00, 0x00')

    def test_maximum_fields(self):
        """Boundary fields must not spill into padding or other operands."""
        cases = [({'a': 12, 'b': 2**32 - 1}, 'ecffffff1f'),
                 ({'a': 1, 'b': 2**21 - 1}, 'e1ffff03'),
                 ({'a': 25, 'b': 2**21 - 1, 'c': 2**21 - 1},
                  'f9ffffffff7f')]
        for fields, expected in cases:
            self.assertEqual(encode_instruction(fields).hex(), expected)

    def test_invalid_intermediate(self):
        """The encoder validates its input independently of the JSON parser."""
        cases = [{'a': 0}, {'a': True, 'b': 1}, {'a': 12},
                 {'a': 1, 'b': 0, 'c': 1}, {'a': 12, 'b': -1},
                 {'a': 25, 'b': 0, 'c': 2**21}]
        for fields in cases:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                encode_instruction(fields)

    def test_empty_program(self):
        """An empty program produces no bytes."""
        self.assertEqual(encode_program([]), [])
