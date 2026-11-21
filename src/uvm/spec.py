"""Instruction fields and machine limits from variant 9."""


opcode_bits = 5
address_bits = 21
word_bits = 32
word_mask = (1 << word_bits) - 1
address_limit = (1 << address_bits) - 1
minimum = 0
instructions = {
    'load_const': (12, 5, ('value',), (word_bits,)),
    'read': (1, 4, ('address',), (address_bits,)),
    'write': (2, 4, ('address',), (address_bits,)),
    'not': (25, 6, ('destination', 'source'), (address_bits, address_bits)),
}


def check_unsigned(value, bits, label):
    """Reject booleans, non-integers and values outside an unsigned field."""
    maximum = (1 << bits) - 1
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f'{label}: expected integer 0..{maximum}')
    return value
