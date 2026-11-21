"""Encode variable-length UVM instructions in little-endian byte order."""

from .spec import check_unsigned, instructions, minimum, opcode_bits


by_opcode = {item[0]: item for item in instructions.values()}


def encode_instruction(fields):
    """Pack validated A/B/C fields with zero-filled unused high bits."""
    opcode = fields.get('a')
    if type(opcode) is not int or opcode not in by_opcode:
        raise ValueError(f'unknown opcode: {opcode}')
    _, size, operands, widths = by_opcode[opcode]
    names = ('b', 'c')[:len(operands)]
    if set(fields) != {'a', *names}:
        raise ValueError('incorrect intermediate fields')
    value, offset = opcode, opcode_bits
    for name, width in zip(names, widths):
        value |= check_unsigned(fields[name], width, name) << offset
        offset += width
    return value.to_bytes(size, 'little')


def encode_program(program):
    """Translate every instruction before any output file is changed."""
    return [encode_instruction(fields) for fields in program]


def format_bytes(data):
    """Format an instruction like the hexadecimal tests in the PDF."""
    return ', '.join(f'0x{byte:02X}' for byte in data)


def decode_instruction(data, position):
    """Decode one instruction and reject truncation, opcodes and padding."""
    if type(position) is not int or not minimum <= position < len(data):
        raise ValueError('instruction offset is outside the program')
    opcode = data[position] & ((1 << opcode_bits) - 1)
    if opcode not in by_opcode:
        raise ValueError(f'offset {position}: unknown opcode {opcode}')
    _, size, operands, widths = by_opcode[opcode]
    following = position + size
    if following > len(data):
        raise ValueError(f'offset {position}: truncated instruction')
    packed = int.from_bytes(data[position:following], 'little')
    offset = opcode_bits
    fields = {'a': opcode}
    for name, width in zip(('b', 'c'), widths):
        fields[name] = (packed >> offset) & ((1 << width) - 1)
        offset += width
    if packed >> offset:
        raise ValueError(f'offset {position}: nonzero reserved bits')
    return fields, following
