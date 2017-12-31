import sys
from decimal import Decimal

PYTHON_MAJOR_VER = sys.version_info[0]

if PYTHON_MAJOR_VER == 3:
    def ord(c):
        return c

def bytes2long(b):
    n = 0
    for c in b:
        n <<= 8
        n += ord(c)
    return n


def decimal64_to_decimal(b):
    "decimal64 bytes to Decimal"
    # https://en.wikipedia.org/wiki/Decimal64_floating-point_format#Densely_packed_decimal_significand_field
    return b

def decimal128_to_decimal(b):
    "decimal128 bytes to Decimal"
    # https://en.wikipedia.org/wiki/Decimal128_floating-point_format#Densely_packed_decimal_significand_field
    sign = 1 if ord(b[0]) & 0x80 else 0
    combination = ((ord(b[0]) & 0x7f) << 10) + (ord(b[1]) << 2) + (ord(b[2]) >> 6)

    if (ord(b[0]) & 0x60) == 0x60:
        exponent = ((ord(b[0]) & 0x1f) * 256 + ord(b[1])) * 2 - 6176
    else:
        exponent = ((ord(b[0]) & 0x7f) * 256 + ord(b[1])) // 2 - 6176

    dpd = bytes2long(b) & 0b11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

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
