"""JSON grammar, operand ranges and exact specification fields."""

import json
import unittest

from src.uvm.parser import format_fields, parse_program


class ParserTests(unittest.TestCase):
    """All four instructions are recognized starting at stage 1."""

    def test_specification(self):
        """Each instruction produces the exact fields in the PDF examples."""
        source = [{'op': 'load_const', 'value': 443},
                  {'op': 'read', 'address': 720},
                  {'op': 'write', 'address': 558},
                  {'op': 'not', 'destination': 724, 'source': 643}]
        expected = [{'a': 12, 'b': 443}, {'a': 1, 'b': 720},
                    {'a': 2, 'b': 558}, {'a': 25, 'b': 724, 'c': 643}]
        self.assertEqual(parse_program(json.dumps(source)), expected)
        self.assertEqual(format_fields(expected[-1]), 'A=25, B=724, C=643')

    def test_bad_structure(self):
        """Reject invalid JSON, unknown commands, missing and extra fields."""
        cases = ['{', '{}', '[null]', '[{"op": []}]',
                 '[{"op":"halt"}]', '[{"op":"read"}]',
                 '[{"op":"read","address":0,"extra":1}]',
                 '[{"op":"read","address":0,"address":1}]']
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_program(text)

    def test_invalid_numbers(self):
        """Booleans and floats are not integers in the assembly language."""
        for value in (-1, 2**32, True, 1.0, '3', None):
            text = json.dumps([{'op': 'load_const', 'value': value}])
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_program(text)

    def test_address_limits(self):
        """Check both 21-bit operands, including NOT's source field."""
        for name, fields in [('read', {'address': 2**21}),
                             ('write', {'address': -1}),
                             ('not', {'destination': 0, 'source': 2**21})]:
            with self.assertRaises(ValueError):
                parse_program(json.dumps([{'op': name, **fields}]))

    def test_valid_boundaries(self):
        """Allow zero and the largest representable values."""
        source = [{'op': 'load_const', 'value': 2**32 - 1},
                  {'op': 'read', 'address': 2**21 - 1},
                  {'op': 'not', 'destination': 0, 'source': 0}]
        self.assertEqual(len(parse_program(json.dumps(source))), 3)
        self.assertEqual(parse_program('[]'), [])
