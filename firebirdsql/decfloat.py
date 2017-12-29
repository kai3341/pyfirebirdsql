from decimal import Decimal
from firebirdsql import srp
from firebirdsql.utils import *

def from_decimal128(d):
    "from Decimal to decimal128 binary"
    sign, digits, exponent = d.as_tuple()
    v = {
        (0, (), 'n'): b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|',         # NaN
        (1, (), 'n'): b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfc',      # -NaN
        (0, (), 'N'): b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00~',         # sNaN
        (1, (), 'N'): b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe',      # -sNaN
        (0, (0, ), 'F'): b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00x',      # Infinity
        (1, (0, ), 'F'): b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf8',   # -Infinity
    }.get((sign, digits, exponent))
    if v:
        return v
    num = 0
    for n in digits:
        num = num * 10 + n
    fraction = from_int112(num)
    if fraction[-1] & 0b00100000:
        exponent = (exponent + 6176) // 2
    else:
        exponent = (exponent + 6176) * 2
    exponent = from_int16(exponent)
    if sign:
        exponent = bytes([exponent[0], exponent[1] | 0x80])

    return fraction + exponent


def to_decimal128(b):
    "decimal 128 bytes to Decimal"
    print()
    for c in b:
        print(bin(byte_to_int(c)), end=' ')
    print()

    sign = 1 if (byte_to_int(b[0]) & 0x80) else 0
    combination = (byte_to_int(b[0]) & 0x7F) * 1024 + byte_to_int(b[1]) * 4 + byte_to_int(b[2]) // 64

    if (b[0] & 0x60) == 0x60:
        exponent = ((b[0] & 0x1f) * 256 + b[1]) * 2 - 6176
    else:
        exponent = ((b[0] & 0x7f) * 256 + b[1]) // 2 - 6176
    if combination & 0b01000000000000000:
        print(combination)
        print('A', combination & 0b00111111111111111)

    digits = srp.bytes2long(b) & 0b11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

    print('sign<%s>combination<%s>digits<%s>' %  (bin(sign), bin(combination), hex(digits)))
    v = {
        (0, 0, 8160): Decimal('NaN'),
        (1, 0, 8160): Decimal('-NaN'),
        (0, 0, 9184): Decimal('sNaN'),
        (1, 0, 9184): Decimal('-sNaN'),
        (0, 0, 6112): Decimal('Infinity'),
        (1, 0, 6112): Decimal('-Infinity'),
    }.get((sign, digits, exponent))
    if v:
        return v
    return Decimal((sign, Decimal(digits).as_tuple()[1], exponent))

def to_uint(b):
    "little endian bytes to unsigned int"
    r = 0
    for n in reversed(b):
        r = r * 256 + n
    return r

