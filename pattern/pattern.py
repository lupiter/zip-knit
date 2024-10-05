import array

from pattern.maths import nibbles, nibbles_per_row, roundeven


class PatternMetadata:
    number: int
    stitches: int
    rows: int
    memo_offset: int
    pattern_offset: int
    pattern_end_offset: int

    def __init__( # pylint: disable=too-many-arguments
            self,
            *,
            number: int,
            stitches: int,
            rows: int,
            memo_offset: int,
            pattern_offset: int,
            pattern_end_offset: int
        ) -> None:
        self.number = number
        self.stitches = stitches
        self.rows = rows
        self.memo_offset = memo_offset
        self.pattern_offset = pattern_offset
        self.pattern_end_offset = pattern_end_offset

    def get_memo(self, data):
        memos = array.array("B")
        rows = self.rows
        memlen = roundeven(rows) / 2
        # memo is padded to en even byte
        for i in range(self.memo_offset, self.memo_offset - memlen, -1):
            msn, lsn = nibbles(data[i])
            memos.append(lsn)
            rows = rows - 1
            if rows:
                memos.append(msn)
                rows = rows - 1
        return memos

    def get_data(self, data: bytes):
        pattern = []

        # print 'patoff = 0x%04X' % patoff
        # print 'rows = ', rows
        # print 'stitches = ', stitches
        for i in range(0, self.rows):
            arow = self.__get_row_data(data, i)
            # print arow
            pattern.append(arow)
        return pattern

    def __get_row_data(self, data: bytes, rownumber: int) -> bytes:
        row = array.array("B")
        nibspr = nibbles_per_row(self.stitches)
        startnib = int(nibspr * rownumber)
        endnib = int(startnib + nibspr)

        for i in range(startnib, endnib, 1):
            nib = self.__get_indexed_nibble(data, i)
            row.append(nib & 0x01)
            stitches = stitches - 1
            if stitches:
                row.append((nib & 0x02) >> 1)
                stitches = stitches - 1
            if stitches:
                row.append((nib & 0x04) >> 2)
                stitches = stitches - 1
            if stitches:
                row.append((nib & 0x08) >> 3)
                stitches = stitches - 1
        return row

    def __get_indexed_nibble(self, data: bytes, nibble: int) -> int:
        # nibbles is zero based
        byte_data = int(nibble / 2)
        m, l = nibbles(data[self.pattern_offset - byte_data])
        if nibble % 2:
            return m
        return l
