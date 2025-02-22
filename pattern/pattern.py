from pattern.maths import nibbles, nibbles_per_row, roundeven


class PatternMetadata:
    number: int
    stitches: int
    rows: int
    memo_offset: int
    pattern_offset: int
    pattern_end_offset: int
    data: bytes

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        number: int,
        stitches: int,
        rows: int,
        memo_offset: int,
        pattern_offset: int,
        pattern_end_offset: int,
        data: bytes
    ) -> None:
        self.number = number
        self.stitches = stitches
        self.rows = rows
        self.memo_offset = memo_offset
        self.pattern_offset = pattern_offset
        self.pattern_end_offset = pattern_end_offset
        self.data = data

    def __eq__(self, other):
        return (
            self.number == other.number
            and self.stitches == other.stitches
            and self.rows == other.rows
            and self.memo_offset == other.memo_offset
            and self.pattern_offset == other.pattern_offset
            and self.pattern_end_offset == other.pattern_end_offset
        )

    def get_memo(self, data: bytes) -> bytes:
        memos = []
        rows = self.rows
        memlen = int(roundeven(rows) / 2)
        # memo is padded to en even byte
        for i in range(self.memo_offset, self.memo_offset - memlen, -1):
            msn, lsn = nibbles(data[i])
            memos.append(lsn)
            rows = rows - 1
            if rows:
                memos.append(msn)
                rows = rows - 1
        return bytes(memos)

    @staticmethod
    def get_data(stitches: int, rows: int, data: bytes, pattern_offset: int) -> list[bytes]:
        pattern = []

        for i in range(0, rows):
            arow = PatternMetadata.__get_row_data(stitches, data, i, pattern_offset)
            pattern.append(arow)
        return pattern

    @staticmethod
    def __get_row_data(stitches: int, data: bytes, rownumber: int, pattern_offset: int) -> bytes:
        row = []
        nibspr = nibbles_per_row(stitches)
        startnib = int(nibspr * rownumber)
        endnib = int(startnib + nibspr)
        stitch = stitches

        for i in range(startnib, endnib, 1):
            nib = PatternMetadata.__get_indexed_nibble(data, i, pattern_offset)
            row.append(nib & 0x01)
            stitch = stitch - 1
            if stitch:
                row.append((nib & 0x02) >> 1)
                stitch = stitch - 1
            if stitch:
                row.append((nib & 0x04) >> 2)
                stitch = stitch - 1
            if stitch:
                row.append((nib & 0x08) >> 3)
                stitch = stitch - 1
        return bytes(row)

    @staticmethod
    def __get_indexed_nibble(data: bytes, nibble: int, pattern_offset: int) -> int:
        # nibbles is zero based
        byte_data = int(nibble / 2)
        msn, lsn = nibbles(data[pattern_offset - byte_data])
        if nibble % 2:
            return msn
        return lsn
