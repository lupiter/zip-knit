def nibbles(achar: int) -> tuple[int, int]:
    # print('0x%02X' % achar)
    msn = (achar & 0xF0) >> 4
    lsn = achar & 0x0F
    return msn, lsn


def hto(hundreds: int, tens: int, ones: int) -> int:
    return (100 * hundreds) + (10 * tens) + ones


def roundeven(val: int) -> int:
    return int((val + (val % 2)))


def roundeight(val: int) -> int:
    if val % 8:
        return int(val + (8 - (val % 8)))
    return val


def roundfour(val: int) -> int:
    if val % 4:
        return int(val + (4 - (val % 4)))
    return val


def nibbles_per_row(stitches: int) -> int:
    # there are four stitches per nibble
    # each row is nibble aligned
    return roundfour(stitches) / 4


def bytes_per_pattern(stitches: int, rows: int) -> int:
    nibbs = rows * nibbles_per_row(stitches)
    b = roundeven(nibbs) / 2
    return b


def bytes_for_memo(rows: int) -> int:
    b = roundeven(rows) / 2
    return b


def bytes_per_pattern_and_memo(stitches: int, rows: int) -> int:
    patbytes = bytes_per_pattern(stitches, rows)
    memobytes = bytes_for_memo(rows)
    return patbytes + memobytes
