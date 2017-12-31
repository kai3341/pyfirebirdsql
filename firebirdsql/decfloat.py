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

def dpd2int(dpd):
    """
    Convert DPD encodined value to int (0-999)
    dpd: DPD encoded value. 10bit unsigned int
    """
    b = [None] * 10
    b[9] = 1 if dpd & 0b1000000000 else 0
    b[8] = 1 if dpd & 0b0100000000 else 0
    b[7] = 1 if dpd & 0b0010000000 else 0
    b[6] = 1 if dpd & 0b0001000000 else 0
    b[5] = 1 if dpd & 0b0000100000 else 0
    b[4] = 1 if dpd & 0b0000010000 else 0
    b[3] = 1 if dpd & 0b0000001000 else 0
    b[2] = 1 if dpd & 0b0000000100 else 0
    b[1] = 1 if dpd & 0b0000000010 else 0
    b[0] = 1 if dpd & 0b0000000001 else 0

    d = [None] * 3
    if b[3] == 0:
        d[2] = b[9] * 4 + b[8] * 2 + b[7]
        d[1] = b[6] * 4 + b[5] * 2 + b[4]
        d[0] = b[2] * 4 + b[1] * 2 + b[0]
    elif (b[3], b[2], b[1]) == (1, 0, 0):
        d[2] = b[9] * 4 + b[8] * 2 + b[7]
        d[1] = b[6] * 4 + b[5] * 2 + b[4]
        d[0] = 8 + b[0]
    elif (b[3], b[2], b[1]) == (1, 0, 1):
        d[2] = b[9] * 4 + b[8] * 2 + b[7]
        d[1] = 8 + b[4]
        d[0] = b[6] * 4 + b[5] * 2 + b[0]
    elif (b[3], b[2], b[1]) == (1, 1, 0):
        d[2] = 8 + b[7]
        d[1] = b[6] * 4 + b[5] * 2 + b[4]
        d[0] = b[9] * 4 + b[8] * 2 + b[0]
    elif (b[6], b[5], b[3], b[2], b[1]) == (0, 0, 1, 1, 1):
        d[2] = 8 + b[7]
        d[1] = 8 + b[4]
        d[0] = b[9] * 4 + b[8] * 2 + b[0]
    elif (b[6], b[5], b[3], b[2], b[1]) == (0, 1, 1, 1, 1):
        d[2] = 8 + b[7]
        d[1] = b[9] * 4 + b[8] * 2 + b[4]
        d[0] = 8 + b[0]
    elif (b[6], b[5], b[3], b[2], b[1]) == (1, 0, 1, 1, 1):
        d[2] = b[9] * 4 + b[8] * 2 + b[7]
        d[1] = 8 + b[4]
        d[0] = 8 + b[0]
    elif (b[6], b[5], b[3], b[2], b[1]) == (1, 1, 1, 1, 1):
        d[2] = 8 + b[7]
        d[1] = 8 + b[4]
        d[0] = 8 + b[0]
    else:
        raise ValueError('Invalid DPD encoding')

    return d[2] * 100 + d[1] * 10 + d[0]


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
