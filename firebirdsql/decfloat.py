from __future__ import print_function

from decimal import Decimal
from firebirdsql import srp
from firebirdsql.utils import *


def decimal64_to_decimal(b):
    "decimal64 bytes to Decimal"
    # https://en.wikipedia.org/wiki/Decimal64_floating-point_format#Densely_packed_decimal_significand_field
    print()
    for c in b:
        print(bin(byte_to_int(c)), end=' ')
    print()
    return b

def decimal128_to_decimal(b):
    "decimal128 bytes to Decimal"
    # https://en.wikipedia.org/wiki/Decimal128_floating-point_format#Densely_packed_decimal_significand_field
    print()
    for c in b:
        print(bin(byte_to_int(c)), end=' ')
    print()
    sign = 1 if (byte_to_int(b[0]) & 0x80) else 0
    combination = ((byte_to_int(b[0]) & 0x7f) << 10) + (byte_to_int(b[1]) << 2) + (byte_to_int(b[2]) >> 6)

    if (byte_to_int(b[0]) & 0x60) == 0x60:
        exponent = ((byte_to_int(b[0]) & 0x1f) * 256 + byte_to_int(b[1])) * 2 - 6176
    else:
        exponent = ((byte_to_int(b[0]) & 0x7f) * 256 + byte_to_int(b[1])) // 2 - 6176

    dpd = srp.bytes2long(b) & 0b11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

    print('sign<%s>combination<%s>dpd<%s>' %  (bin(sign), bin(combination), bin(dpd)))
    v = {
        (0, 0, 8160): Decimal('NaN'),
        (1, 0, 8160): Decimal('-NaN'),
        (0, 0, 9184): Decimal('sNaN'),
        (1, 0, 9184): Decimal('-sNaN'),
        (0, 0, 6112): Decimal('Infinity'),
        (1, 0, 6112): Decimal('-Infinity'),
    }.get((sign, dpd, exponent))
    if v:
        return v
    return Decimal((sign, Decimal(dpd).as_tuple()[1], exponent))
