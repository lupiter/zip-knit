class PatternMetadata:
    number: int
    stitches: int
    rows: int
    memo_offset: int
    pattern_offset: int
    pattern_end_offset: int

    def __init__( # pylint: disable=too-many-arguments
            self,
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

    


