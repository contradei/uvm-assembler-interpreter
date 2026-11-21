"""Separate immutable instruction bytes from sparse 32-bit data memory."""

from .codec import decode_instruction
from .spec import address_bits, check_unsigned, word_bits


class Memory:
    """Model all 21-bit addresses, with implicit zero in unwritten cells."""

    def __init__(self):
        """Start with no assigned cells."""
        self.cells = {}

    def read(self, address):
        """Read a valid address without allocating unwritten cells."""
        check_unsigned(address, address_bits, 'address')
        return self.cells.get(address, 0)

    def write(self, address, value):
        """Store a word after validating both the address and its value."""
        check_unsigned(address, address_bits, 'address')
        check_unsigned(value, word_bits, 'word')
        self.cells[address] = value


class Machine:
    """Execute a program sequentially until the bytecode ends."""

    def __init__(self, code):
        """Initialize a zero accumulator and independent data memory."""
        self.code = bytes(code)
        self.memory = Memory()
        self.accumulator = 0
        self.position = 0
        self.executed = 0

    def execute(self, fields):
        """Dispatch basic memory operations; NOT is reserved for stage 4."""
        handlers = {12: self.load_constant, 1: self.read, 2: self.write}
        handler = handlers.get(fields['a'])
        if handler is None:
            raise ValueError('NOT execution is available starting at stage 4')
        handler(fields)

    def load_constant(self, fields):
        """Copy B into the accumulator."""
        self.accumulator = fields['b']

    def read(self, fields):
        """Copy data memory at B into the accumulator."""
        self.accumulator = self.memory.read(fields['b'])

    def write(self, fields):
        """Copy the accumulator into data memory at B."""
        self.memory.write(fields['b'], self.accumulator)

    def run(self):
        """Read, decode and execute complete instructions in byte order."""
        while self.position < len(self.code):
            fields, following = decode_instruction(self.code, self.position)
            self.execute(fields)
            self.position = following
            self.executed += 1
        return self.memory
