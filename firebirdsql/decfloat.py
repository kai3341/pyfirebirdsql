from decimal import Decimal
from firebirdsql import srp
from firebirdsql.utils import *

def to_decimal128(b):
    "decimal 128 bytes to Decimal"
    # https://en.wikipedia.org/wiki/Decimal128_floating-point_format#Densely_packed_decimal_significand_field
    print()
    for c in b:
        print(bin(byte_to_int(c)), end=' ')
    print()
    sign = 1 if (byte_to_int(b[0]) & 0x80) else 0
    combination = ((byte_to_int(b[0]) & 0x7f) << 10) + (byte_to_int(b[1]) << 2) + (byte_to_int(b[2]) >> 6)

    if (b[0] & 0x60) == 0x60:
        exponent = ((b[0] & 0x1f) * 256 + b[1]) * 2 - 6176
    else:
        exponent = ((b[0] & 0x7f) * 256 + b[1]) // 2 - 6176

    digits = srp.bytes2long(b) & 0b11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

    print('sign<%s>combination<%s>digits<%s>' %  (bin(sign), bin(combination), bin(digits)))
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
