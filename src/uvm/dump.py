"""Serialize an inclusive address range as a UTF-8 XML memory dump."""

from xml.etree import ElementTree

from .spec import address_bits, check_unsigned


def validate_range(start, end):
    """Require ordered inclusive endpoints in the 21-bit address space."""
    check_unsigned(start, address_bits, 'start')
    check_unsigned(end, address_bits, 'end')
    if start > end:
        raise ValueError('start must not exceed end')


def memory_xml(memory, start, end):
    """Include each requested cell, including zeros, with explicit addresses."""
    validate_range(start, end)
    root = ElementTree.Element('memory', start=str(start), end=str(end))
    for address in range(start, end + 1):
        ElementTree.SubElement(root, 'cell', address=str(address),
                               value=str(memory.read(address)))
    ElementTree.indent(root, space='  ')
    return ElementTree.tostring(root, encoding='utf-8', xml_declaration=True)
