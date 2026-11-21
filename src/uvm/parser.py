"""Translate strict JSON assembly into dictionaries of instruction fields."""

import json
from pathlib import Path

from .spec import check_unsigned, instructions


def unique_object(pairs):
    """Reject duplicate JSON keys instead of silently losing an operand."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def parse_instruction(command):
    """Validate a mnemonic and map named operands to fields a, b and c."""
    if not isinstance(command, dict):
        raise ValueError('instruction must be an object')
    name = command.get('op')
    if not isinstance(name, str) or name not in instructions:
        raise ValueError(f'unknown instruction: {name}')
    opcode, size, operands, widths = instructions[name]
    if set(command) != {'op', *operands}:
        raise ValueError(f'{name}: expected fields op, {", ".join(operands)}')
    fields = {'a': opcode}
    for field, operand, width in zip(('b', 'c'), operands, widths):
        fields[field] = check_unsigned(command[operand], width, operand)
    return fields


def parse_program(text):
    """Read a JSON array and annotate errors with the instruction number."""
    data = json.loads(text, object_pairs_hook=unique_object)
    if not isinstance(data, list):
        raise ValueError('program must be a JSON array')
    program = []
    for number, command in enumerate(data, 1):
        try:
            program.append(parse_instruction(command))
        except ValueError as error:
            raise ValueError(f'instruction {number}: {error}') from error
    return program


def read_program(path):
    """Load UTF-8 JSON; accept an optional BOM from Windows editors."""
    return parse_program(Path(path).read_text(encoding='utf-8-sig'))


def format_fields(fields):
    """Display field names in the exact A=..., B=..., C=... test notation."""
    return ', '.join(f'{key.upper()}={value}' for key, value in fields.items())
