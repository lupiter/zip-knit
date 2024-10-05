import unittest

from pattern.pattern import PatternMetadata


class TestPattern(unittest.TestCase):
    def test_get_memo(self):
        pattern = PatternMetadata(
            number=1,
            stitches=8,
            rows=1,
            memo_offset=8,
            pattern_offset=16,
            pattern_end_offset=32,
        )
        memo = pattern.get_memo(list(range(32)))
        self.assertEqual(memo, ["B", 8])

    def test_get_data(self):
        pattern = PatternMetadata(
            number=1,
            stitches=8,
            rows=1,
            memo_offset=8,
            pattern_offset=16,
            pattern_end_offset=32,
        )
        data = pattern.get_data(list(range(32)))
        self.assertEqual(data, [["B", 0, 0, 0, 0, 1, 0, 0, 0]])

        pattern = PatternMetadata(
            number=1,
            stitches=1,
            rows=8,
            memo_offset=8,
            pattern_offset=16,
            pattern_end_offset=32,
        )
        data = pattern.get_data(list(range(32)))
        self.assertEqual(
            data,
            [
                ["B", 0],
                ["B", 1],
                ["B", 1],
                ["B", 0],
                ["B", 0],
                ["B", 0],
                ["B", 1],
                ["B", 0],
            ],
        )
